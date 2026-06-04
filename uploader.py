"""
uploader.py — Secure Channel Publisher Engine (v7.0 - BUG FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fix: selfDeclaredMadeWithAI removed — YouTube Data API v3 mein yeh field exist nahi karta,
     HTTP 400 invalidParameter error deta tha.
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
    creds = None
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    token_json_str = os.environ.get("YOUTUBE_TOKEN_JSON")

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

    token_file_path = Path("token.json")
    if not creds and token_file_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file_path), scopes)
        except Exception as exc:
            logger.warning(f"Local token file parsing failed: {exc}")

    if creds and creds.expired and creds.refresh_token:
        try:
            logger.info("YouTube session expired. Refreshing token...")
            creds.refresh(Request())
            if token_file_path.exists():
                with open(token_file_path, "w") as tf:
                    tf.write(creds.to_json())
        except Exception as rex:
            logger.error(f"Token refresh failed: {rex}")
            creds = None

    if not creds:
        secret_path = Path("client_secrets.json")
        if secret_path.exists():
            logger.info("Starting local OAuth flow for YouTube...")
            flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), scopes)
            creds = flow.run_local_server(port=0)
            with open(token_file_path, "w") as tf:
                tf.write(creds.to_json())
            logger.info("Fresh token saved to token.json")
        else:
            logger.warning("YouTube auth keys missing. Skipping upload.")
            return None

    return build("youtube", "v3", credentials=creds)


def upload_to_cloudinary(file_path: str, resource_type: str = "video") -> dict:
    try:
        logger.info(f"Uploading {resource_type} to Cloudinary...")
        upload_result = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type,
            folder="yt_automation",
            overwrite=True,
            invalidate=True,
        )
        url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
        logger.info(f"✅ Cloudinary {resource_type} upload successful: {url}")
        return {"url": url, "public_id": public_id}
    except Exception as e:
        logger.error(f"Cloudinary {resource_type} upload error: {e}")
        return {"url": None, "public_id": None}


def set_youtube_thumbnail_local(youtube, video_id: str, local_thumb_path: str):
    try:
        logger.info(f"Uploading thumbnail from: {local_thumb_path}")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(local_thumb_path, mimetype="image/jpeg"),
        ).execute()
        logger.info("✅ YouTube thumbnail set successfully!")
    except Exception as e:
        logger.error(f"YouTube thumbnail upload failed: {e}")


def cleanup_cloudinary(public_id: str, resource_type: str = "video"):
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        logger.info(f"✅ Cloudinary cleanup done: {public_id}")
    except Exception as e:
        logger.error(f"Cloudinary cleanup error: {e}")


def upload_all_platforms(video_path: str, seo: dict, thumbnail_path: str = None) -> dict:
    logger.info(f"Initiating publisher engine for: {video_path}")

    timestamp_fallback = datetime.now().strftime("%I:%M%p").lstrip("0")
    title = seo.get("title") or f"Dark Psychology Fact {timestamp_fallback}"
    title = title.split("#")[0].strip()[:100]

    description = seo.get("description", "Explore the hidden truths of human psychology.")
    hashtags = seo.get("hashtags", ["#DarkPsychology", "#Mindset", "#Shorts"])

    if "#Shorts" not in hashtags and "#shorts" not in hashtags:
        hashtags.append("#Shorts")

    full_description = f"{description}\n\n" + " ".join(hashtags)
    results = {"youtube": "skipped", "facebook": "skipped", "instagram": "skipped"}

    cloudinary_data = upload_to_cloudinary(video_path, resource_type="video")
    cloudinary_url = cloudinary_data["url"]
    cloudinary_public_id = cloudinary_data["public_id"]

    if not cloudinary_url:
        logger.error("Cloudinary video upload failed — aborting Meta uploads.")
        return results

    cloud_thumb_url = None
    cloud_thumb_id = None
    if thumbnail_path and os.path.exists(thumbnail_path):
        thumb_cloud_data = upload_to_cloudinary(thumbnail_path, resource_type="image")
        cloud_thumb_url = thumb_cloud_data["url"]
        cloud_thumb_id = thumb_cloud_data["public_id"]

    youtube = _get_youtube_service()
    if not youtube:
        logger.warning("YouTube API service skipped.")
        results["youtube"] = "saved_locally_without_upload"
    else:
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": full_description,
                    "tags": [tag.replace("#", "").strip() for tag in hashtags if tag.startswith("#")],
                    "categoryId": "22",
                    "defaultAudioLanguage": "en-US",
                    "defaultLanguage": "en-US",
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                    # FIX: selfDeclaredMadeWithAI hata diya
                    # YouTube Data API v3 mein yeh field valid nahi hai
                    # iska hona HTTP 400 invalidParameter error deta tha
                },
            }

            media = MediaFileUpload(
                str(video_path),
                chunksize=1024 * 1024 * 2,
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
            while response is None:
                status_chunk, response = request.next_chunk()

            youtube_id = response.get("id")
            logger.info(f"✅ YouTube Upload Successful! Video ID: {youtube_id}")
            results["youtube"] = f"success_id_{youtube_id}"

            if youtube_id and thumbnail_path and os.path.exists(thumbnail_path):
                set_youtube_thumbnail_local(youtube, youtube_id, thumbnail_path)

        except Exception as err:
            logger.error(f"YouTube upload failed: {err}")
            results["youtube"] = f"failed: {str(err)}"

    meta_caption = f"{title}\n\n{full_description}"

    if META_TOKEN and FB_PAGE_ID and cloudinary_url:
        results["facebook"] = post_to_facebook_via_url(cloudinary_url, cloud_thumb_url, meta_caption)
    else:
        logger.warning("Facebook skipped: Missing token, Page ID, or Cloudinary URL.")

    if META_TOKEN and IG_ACCT_ID and cloudinary_url:
        results["instagram"] = post_to_instagram_via_url(cloudinary_url, cloud_thumb_url, meta_caption)
    else:
        logger.warning("Instagram skipped: Missing token, ID, or Cloudinary URL.")

    if cloudinary_public_id or cloud_thumb_id:
        logger.info("Waiting 3 minutes for Meta processing...")
        time.sleep(180)
        if cloudinary_public_id:
            cleanup_cloudinary(cloudinary_public_id, resource_type="video")
        if cloud_thumb_id:
            cleanup_cloudinary(cloud_thumb_id, resource_type="image")

    return results


def post_to_facebook_via_url(video_url: str, thumb_url: str, caption: str) -> str:
    try:
        url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/videos"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        payload = {
            "description": caption,
            "file_url": video_url,
            "access_token": META_TOKEN,
        }
        if thumb_url:
            payload["thumb_url"] = thumb_url

        res = requests.post(url, data=payload, headers=headers, timeout=60).json()
        if "id" in res:
            logger.info(f"✅ Facebook Upload Successful! ID: {res['id']}")
            return f"success_id_{res['id']}"
        logger.error(f"Facebook upload failed: {res}")
        return f"failed: {json.dumps(res)}"
    except Exception as e:
        logger.error(f"Facebook upload exception: {e}")
        return f"failed_exception: {str(e)}"


def post_to_instagram_via_url(video_url: str, thumb_url: str, caption: str) -> str:
    try:
        container_url = f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": META_TOKEN,
        }

        if thumb_url:
            payload["cover_url"] = thumb_url
            logger.info("🎯 Custom cover image set for Instagram Reel.")
        else:
            payload["cover_frame_time"] = 2000

        req = requests.post(container_url, data=payload, headers=headers, timeout=60)
        res_data = req.json()
        creation_id = res_data.get("id")

        if not creation_id:
            logger.error(f"Instagram container creation failed: {res_data}")
            return f"failed_container_creation: {json.dumps(res_data)}"

        logger.info("Checking Instagram processing status...")
        for i in range(15):
            time.sleep(15)
            status_res = requests.get(
                f"https://graph.facebook.com/v20.0/{creation_id}",
                params={"fields": "status_code", "access_token": META_TOKEN},
                headers=headers,
            ).json()
            status = status_res.get("status_code")
            logger.info(f"Instagram status check {i + 1}/15: {status}")

            if status == "FINISHED":
                break
            elif status == "ERROR":
                logger.error(f"Instagram processing error: {status_res}")
                return f"failed_processing_error: {json.dumps(status_res)}"

        publish_url = f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media_publish"
        res = requests.post(
            publish_url,
            data={"creation_id": creation_id, "access_token": META_TOKEN},
            headers=headers,
            timeout=60,
        )
        pub_data = res.json()

        if "id" in pub_data:
            logger.info(f"✅ Instagram Reel Published! ID: {pub_data['id']}")
            return f"success_id_{pub_data['id']}"
        else:
            logger.error(f"Instagram publish failed: {pub_data}")
            return f"failed_publish_error: {json.dumps(pub_data)}"

    except Exception as e:
        logger.error(f"Instagram upload exception: {e}")
        return f"failed_exception: {str(e)}"
