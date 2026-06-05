"""
uploader.py — Secure Channel Publisher Engine (v7.2 - SCHEDULED PUBLISHING)
Khateb Ishq Pipeline & Production Matrix Sync
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
from datetime import datetime, timezone
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
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

META_TOKEN = os.environ.get("META_ACCESS_TOKEN")
FB_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
IG_ACCT_ID = os.environ.get("INSTAGRAM_BUSINESS_ID")

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True,
)


def _get_youtube_service():
    creds  = None
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    client_id      = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret  = os.environ.get("YOUTUBE_CLIENT_SECRET")
    token_json_str = os.environ.get("YOUTUBE_TOKEN_JSON")
    token_file     = Path("token.json")

    if token_json_str:
        try:
            token_data = json.loads(token_json_str)
            refresh_token = token_data.get("refresh_token")
            if refresh_token and client_id and client_secret:
                logger.info("Rebuilding credentials from GitHub Secrets...")
                creds = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=client_id,
                    client_secret=client_secret,
                )
        except Exception as exc:
            logger.warning(f"Credentials parsing failed: {exc}")

    if not creds and token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), scopes)
        except Exception as exc:
            logger.warning(f"Local token file failed: {exc}")

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            if token_file.exists():
                with open(token_file, "w") as tf:
                    tf.write(creds.to_json())
        except Exception as rex:
            logger.error(f"Token refresh failed: {rex}")
            creds = None

    if not creds:
        secret_path = Path("client_secrets.json")
        if secret_path.exists():
            flow  = InstalledAppFlow.from_client_secrets_file(str(secret_path), scopes)
            creds = flow.run_local_server(port=0)
            with open(token_file, "w") as tf:
                tf.write(creds.to_json())
        else:
            logger.warning("YouTube auth keys missing. Skipping upload.")
            return None

    return build("youtube", "v3", credentials=creds)


def upload_to_cloudinary(file_path: str, resource_type: str = "video") -> dict:
    try:
        logger.info(f"Uploading {resource_type} to Cloudinary...")
        result = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type,
            folder="khateb_ishq",
            overwrite=True,
            invalidate=True,
        )
        url       = result.get("secure_url")
        public_id = result.get("public_id")
        logger.info(f"✅ Cloudinary {resource_type}: {url}")
        return {"url": url, "public_id": public_id}
    except Exception as e:
        logger.error(f"Cloudinary error: {e}")
        return {"url": None, "public_id": None}


def cleanup_cloudinary(public_id: str, resource_type: str = "video"):
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        logger.info(f"✅ Cloudinary cleanup: {public_id}")
    except Exception as e:
        logger.error(f"Cloudinary cleanup error: {e}")


def upload_to_youtube(video_path: str, seo: dict, publish_at: str = None) -> str:
    youtube = _get_youtube_service()
    if not youtube:
        return "skipped_no_auth"

    title    = seo.get("title", "Khateb Ishq")[:100]
    hashtags = seo.get("hashtags", ["#SadShayari", "#Shorts"])
    desc     = seo.get("description", "")

    if "#Shorts" not in hashtags and "#shorts" not in hashtags:
        hashtags.append("#Shorts")

    full_description = f"{desc}\n\n" + " ".join(hashtags)

    try:
        if publish_at:
            privacy_status = "private"
            logger.info(f"📅 Scheduling YouTube video: {publish_at}")
        else:
            privacy_status = "public"
            logger.info("📤 Publishing YouTube video immediately.")

        body = {
            "snippet": {
                "title":                title,
                "description":          full_description,
                "tags":                 [t.replace("#", "").strip() for t in hashtags if t.startswith("#")],
                "categoryId":           "22",
                "defaultAudioLanguage": "ur",
                "defaultLanguage":      "ur",
            },
            "status": {
                "privacyStatus":           privacy_status,
                "selfDeclaredMadeForKids": False,
                **({"publishAt": publish_at} if publish_at else {})
            }
        }

        media   = MediaFileUpload(
            str(video_path),
            chunksize=1024 * 1024 * 2,
            resumable=True,
            mimetype="video/mp4"
        )
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            _, response = request.next_chunk()

        video_id = response.get("id")
        logger.info(f"✅ YouTube done! ID: {video_id} | Scheduled: {publish_at or 'Immediate'}")
        return f"success_id_{video_id}"

    except Exception as err:
        logger.error(f"YouTube upload failed: {err}")
        return f"failed: {str(err)}"


def post_to_facebook_via_url(video_url: str, thumb_url: str, caption: str) -> str:
    try:
        url     = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/videos"
        headers = {
            "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
        }
        payload = {
            "description":  caption,
            "file_url":     video_url,
            "access_token": META_TOKEN,
        }
        if thumb_url:
            payload["thumb_url"] = thumb_url

        res = requests.post(url, data=payload, headers=headers, timeout=60).json()
        if "id" in res:
            logger.info(f"✅ Facebook! ID: {res['id']}")
            return f"success_id_{res['id']}"
        logger.error(f"Facebook failed: {res}")
        return f"failed: {json.dumps(res)}"
    except Exception as e:
        return f"failed_exception: {str(e)}"


def post_to_instagram_via_url(video_url: str, thumb_url: str, caption: str) -> str:
    try:
        container_url = f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media"
        headers       = {
            "User-Agent":      "Mozilla/5.0 (Linux; Android 13; SM-S918B)",
            "Accept-Language": "en-US,en;q=0.9",
        }
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

        res_data    = requests.post(container_url, data=payload,
                                    headers=headers, timeout=60).json()
        creation_id = res_data.get("id")

        if not creation_id:
            return f"failed_container: {json.dumps(res_data)}"

        for i in range(15):
            time.sleep(15)
            status = requests.get(
                f"https://graph.facebook.com/v20.0/{creation_id}",
                params={"fields": "status_code", "access_token": META_TOKEN},
                headers=headers
            ).json().get("status_code")
            logger.info(f"Instagram status {i+1}/15: {status}")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                return "failed_processing"

        pub = requests.post(
            f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media_publish",
            data={"creation_id": creation_id, "access_token": META_TOKEN},
            headers=headers, timeout=60
        ).json()

        if "id" in pub:
            logger.info(f"✅ Instagram Reel! ID: {pub['id']}")
            return f"success_id_{pub['id']}"
        return f"failed_publish: {json.dumps(pub)}"

    except Exception as e:
        return f"failed_exception: {str(e)}"


def upload_all_platforms(
    video_path: str,
    seo: dict,
    thumbnail_path: str = None,
    publish_at: str = None
) -> dict:
    logger.info(f"Initiating publisher for: {video_path}")
    results = {"youtube": "skipped", "facebook": "skipped", "instagram": "skipped"}

    title    = seo.get("title", "Dark Psychology Secrets")
    hashtags = seo.get("hashtags", ["#darkpsychology", "#shorts"])
    desc     = seo.get("description", "")
    full_desc = f"{desc}\n\n" + " ".join(hashtags)

    # 1. YouTube Execution Route
    results["youtube"] = upload_to_youtube(video_path, seo, publish_at=publish_at)

    # 2. Cloudinary Engine for Meta Staging
    cloud_data      = upload_to_cloudinary(video_path, resource_type="video")
    cloudinary_url  = cloud_data["url"]
    cloud_pub_id    = cloud_data["public_id"]

    if not cloudinary_url:
        logger.error("Cloudinary deployment failed — skipping Meta Hooks.")
        return results

    cloud_thumb_url = None
    cloud_thumb_id  = None
    if thumbnail_path and os.path.exists(thumbnail_path):
        td              = upload_to_cloudinary(thumbnail_path, resource_type="image")
        cloud_thumb_url = td["url"]
        cloud_thumb_id  = td["public_id"]

    meta_caption = f"{title}\n\n{full_desc}"

    # 3. Facebook Route Execution
    if META_TOKEN and FB_PAGE_ID:
        results["facebook"] = post_to_facebook_via_url(
            cloudinary_url, cloud_thumb_url, meta_caption
        )

    # 4. Instagram Route Execution
    if META_TOKEN and IG_ACCT_ID:
        results["instagram"] = post_to_instagram_via_url(
            cloudinary_url, cloud_thumb_url, meta_caption
        )

    # 5. Cloudinary Staging Storage Wiping
    if cloud_pub_id or cloud_thumb_id:
        logger.info("Waiting 3 min for Meta processing nodes before storage cleanup...")
        time.sleep(180)
        if cloud_pub_id:
            cleanup_cloudinary(cloud_pub_id, resource_type="video")
        if cloud_thumb_id:
            cleanup_cloudinary(cloud_thumb_id, resource_type="image")

    return results
