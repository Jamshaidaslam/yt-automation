"""
uploader.py — Secure Channel Publisher Engine (v7.1)
Platforms: YouTube + Facebook + Instagram (Reels)
"""

import json
import logging
import os
import time
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

try:
    import config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False

logger = logging.getLogger(__name__)

META_TOKEN = os.environ.get("META_ACCESS_TOKEN")
FB_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
IG_ACCT_ID = os.environ.get("INSTAGRAM_BUSINESS_ID")

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True,
)


# ══════════════════════════════════════════════════════════════════════════════
def _get_youtube_service():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    client_id      = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret  = os.environ.get("YOUTUBE_CLIENT_SECRET")
    token_json_str = os.environ.get("YOUTUBE_TOKEN_JSON")
    token_file     = Path("token.json")

    creds = None

    # Try environment variable credentials (GitHub Actions / CI)
    if token_json_str:
        try:
            token_data    = json.loads(token_json_str)
            refresh_token = token_data.get("refresh_token")
            if refresh_token and client_id and client_secret:
                logger.info("Rebuilding credentials from environment secrets...")
                creds = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=client_id,
                    client_secret=client_secret,
                )
        except Exception as e:
            logger.warning(f"Env credentials parsing failed: {e}")

    # Try local token file
    if not creds and token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), scopes)
        except Exception as e:
            logger.warning(f"Local token.json parsing failed: {e}")

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            logger.info("Refreshing expired YouTube token...")
            creds.refresh(Request())
            if token_file.exists():
                token_file.write_text(creds.to_json())
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            creds = None

    # Local OAuth flow as last resort
    if not creds:
        secret_path = Path("client_secrets.json")
        if secret_path.exists():
            logger.info("Starting local OAuth flow...")
            flow  = InstalledAppFlow.from_client_secrets_file(str(secret_path), scopes)
            creds = flow.run_local_server(port=0)
            token_file.write_text(creds.to_json())
            logger.info("Fresh token saved to token.json")
        else:
            logger.warning("No YouTube credentials found — skipping upload.")
            return None

    return build("youtube", "v3", credentials=creds)


# ══════════════════════════════════════════════════════════════════════════════
def upload_to_cloudinary(file_path: str, resource_type: str = "video") -> dict:
    try:
        logger.info(f"Uploading {resource_type} to Cloudinary: {Path(file_path).name}")
        result    = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type,
            folder="yt_automation",
            overwrite=True,
            invalidate=True,
        )
        url       = result.get("secure_url")
        public_id = result.get("public_id")
        logger.info(f"✅ Cloudinary upload done: {url}")
        return {"url": url, "public_id": public_id}
    except Exception as e:
        logger.error(f"Cloudinary {resource_type} upload failed: {e}")
        return {"url": None, "public_id": None}


def set_youtube_thumbnail(youtube, video_id: str, thumb_path: str):
    try:
        logger.info(f"Setting YouTube thumbnail from: {thumb_path}")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumb_path, mimetype="image/jpeg"),
        ).execute()
        logger.info("✅ YouTube thumbnail set.")
    except Exception as e:
        logger.error(f"YouTube thumbnail upload failed: {e}")


def cleanup_cloudinary(public_id: str, resource_type: str = "video"):
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        logger.info(f"✅ Cloudinary cleanup: {public_id}")
    except Exception as e:
        logger.error(f"Cloudinary cleanup failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
def upload_all_platforms(video_path: str, seo: dict, thumbnail_path: str = None) -> dict:
    logger.info(f"🚀 Starting upload pipeline for: {video_path}")

    # BUG FIX 1: video_path existence not checked before upload attempts
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return {"youtube": "failed_file_not_found",
                "facebook": "skipped", "instagram": "skipped"}

    timestamp    = datetime.now().strftime("%I:%M%p").lstrip("0")
    title        = (seo.get("title") or f"Short Video {timestamp}").split("#")[0].strip()[:100]
    description  = seo.get("description", "")
    hashtags     = seo.get("hashtags", ["#Shorts"])

    if "#Shorts" not in hashtags and "#shorts" not in hashtags:
        hashtags.append("#Shorts")

    full_description = f"{description}\n\n" + " ".join(hashtags)
    results = {"youtube": "skipped", "facebook": "skipped", "instagram": "skipped"}

    # ── Cloudinary (needed for Meta platforms) ────────────────────────────────
    cloudinary_data      = upload_to_cloudinary(video_path, resource_type="video")
    cloudinary_url       = cloudinary_data["url"]
    cloudinary_public_id = cloudinary_data["public_id"]

    if not cloudinary_url:
        logger.error("Cloudinary video upload failed — Meta uploads skipped.")

    cloud_thumb_url = None
    cloud_thumb_id  = None
    if thumbnail_path and os.path.exists(thumbnail_path):
        thumb_data      = upload_to_cloudinary(thumbnail_path, resource_type="image")
        cloud_thumb_url = thumb_data["url"]
        cloud_thumb_id  = thumb_data["public_id"]

    # ── YouTube ───────────────────────────────────────────────────────────────
    youtube = _get_youtube_service()
    if not youtube:
        results["youtube"] = "skipped_no_credentials"
    else:
        try:
            body = {
                "snippet": {
                    "title":                title,
                    "description":          full_description,
                    "tags":                 [t.replace("#", "").strip() for t in hashtags if t.startswith("#")],
                    "categoryId":           "22",
                    "defaultLanguage":      "en-US",
                    "defaultAudioLanguage": "en-US",
                },
                "status": {
                    "privacyStatus":           "public",
                    "selfDeclaredMadeForKids": False,
                    # NOTE: selfDeclaredMadeWithAI removed — not a valid API field,
                    # caused HTTP 400 invalidParameter error.
                },
            }

            media   = MediaFileUpload(
                video_path,
                chunksize=2 * 1024 * 1024,
                resumable=True,
                mimetype="video/mp4",
            )
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            logger.info(f"Uploading to YouTube: '{title}'")
            response = None

            # BUG FIX 2: No progress logging during chunked upload —
            # long uploads appeared frozen. Now logs each chunk's progress.
            while response is None:
                status_chunk, response = request.next_chunk()
                if status_chunk:
                    pct = int(status_chunk.progress() * 100)
                    logger.info(f"YouTube upload progress: {pct}%")

            yt_id = response.get("id")
            logger.info(f"✅ YouTube upload complete! ID: {yt_id}")
            logger.info(f"   URL: https://www.youtube.com/shorts/{yt_id}")
            results["youtube"] = f"success_id_{yt_id}"

            if yt_id and thumbnail_path and os.path.exists(thumbnail_path):
                set_youtube_thumbnail(youtube, yt_id, thumbnail_path)

        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            results["youtube"] = f"failed: {e}"

    # ── Facebook ──────────────────────────────────────────────────────────────
    meta_caption = f"{title}\n\n{full_description}"

    if META_TOKEN and FB_PAGE_ID and cloudinary_url:
        results["facebook"] = _post_to_facebook(cloudinary_url, cloud_thumb_url, meta_caption)
    else:
        logger.warning("Facebook skipped: missing token / page ID / video URL.")

    # ── Instagram ─────────────────────────────────────────────────────────────
    if META_TOKEN and IG_ACCT_ID and cloudinary_url:
        results["instagram"] = _post_to_instagram(cloudinary_url, cloud_thumb_url, meta_caption)
    else:
        logger.warning("Instagram skipped: missing token / account ID / video URL.")

    # ── Cloudinary cleanup (after Meta has processed) ─────────────────────────
    # BUG FIX 3: sleep(180) always ran even when Meta uploads were skipped —
    # wasted 3 minutes for no reason. Now only sleeps if Meta actually uploaded.
    meta_uploaded = (
        results["facebook"].startswith("success") or
        results["instagram"].startswith("success")
    )
    if meta_uploaded and (cloudinary_public_id or cloud_thumb_id):
        logger.info("Waiting 3 minutes for Meta CDN processing before cleanup...")
        time.sleep(180)

    if cloudinary_public_id:
        cleanup_cloudinary(cloudinary_public_id, resource_type="video")
    if cloud_thumb_id:
        cleanup_cloudinary(cloud_thumb_id, resource_type="image")

    logger.info(f"📊 Upload results: {results}")
    return results


# ══════════════════════════════════════════════════════════════════════════════
def _post_to_facebook(video_url: str, thumb_url: str, caption: str) -> str:
    try:
        payload = {
            "description":  caption,
            "file_url":     video_url,
            "access_token": META_TOKEN,
        }
        if thumb_url:
            payload["thumb_url"] = thumb_url

        res = requests.post(
            f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/videos",
            data=payload,
            timeout=60,
        ).json()

        if "id" in res:
            logger.info(f"✅ Facebook upload done! ID: {res['id']}")
            return f"success_id_{res['id']}"

        logger.error(f"Facebook upload failed: {res}")
        return f"failed: {json.dumps(res)}"

    except Exception as e:
        logger.error(f"Facebook exception: {e}")
        return f"failed_exception: {e}"


def _post_to_instagram(video_url: str, thumb_url: str, caption: str) -> str:
    try:
        # Step 1: Create media container
        payload = {
            "media_type":   "REELS",
            "video_url":    video_url,
            "caption":      caption,
            "access_token": META_TOKEN,
        }
        if thumb_url:
            payload["cover_url"] = thumb_url
        else:
            payload["cover_frame_time"] = 2000

        res_data    = requests.post(
            f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media",
            data=payload,
            timeout=60,
        ).json()
        creation_id = res_data.get("id")

        if not creation_id:
            logger.error(f"Instagram container creation failed: {res_data}")
            return f"failed_container: {json.dumps(res_data)}"

        # Step 2: Poll processing status
        logger.info("Polling Instagram processing status...")
        for i in range(15):
            time.sleep(15)
            status = requests.get(
                f"https://graph.facebook.com/v20.0/{creation_id}",
                params={"fields": "status_code", "access_token": META_TOKEN},
                timeout=30,
            ).json()
            code = status.get("status_code")
            logger.info(f"Instagram status {i+1}/15: {code}")

            if code == "FINISHED":
                break
            if code == "ERROR":
                logger.error(f"Instagram processing error: {status}")
                return f"failed_processing: {json.dumps(status)}"

        # Step 3: Publish
        pub = requests.post(
            f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media_publish",
            data={"creation_id": creation_id, "access_token": META_TOKEN},
            timeout=60,
        ).json()

        if "id" in pub:
            logger.info(f"✅ Instagram Reel published! ID: {pub['id']}")
            return f"success_id_{pub['id']}"

        logger.error(f"Instagram publish failed: {pub}")
        return f"failed_publish: {json.dumps(pub)}"

    except Exception as e:
        logger.error(f"Instagram exception: {e}")
        return f"failed_exception: {e}"
