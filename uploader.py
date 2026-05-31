"""
uploader.py — Secure Channel Publisher Engine (FIXED META PROTOCOL — NO DELAY)
AI Dark Realities · Short-Form Video Pipeline
─────────────────────────────────────────────────────────────────────────────────────
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
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import urllib.request
import io

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

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)


def _get_youtube_service():
    creds = None
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    if os.environ.get("YOUTUBE_TOKEN_JSON"):
        try:
            token_data = json.loads(os.environ.get("YOUTUBE_TOKEN_JSON"))
            creds = Credentials.from_authorized_user_info(token_data, scopes)
        except Exception as exc:
            logger.warning(f"Cloud credentials parsing failed: {exc}")

    token_file_path = Path("token.json")
    if not creds and token_file_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file_path), scopes)
        except Exception as exc:
            logger.warning(f"Local token file parsing failed: {exc}")

    if creds and creds.expired and creds.refresh_token:
        try:
            logger.info("YouTube session expired. Attempting background auto-refresh...")
            creds.refresh(Request())
            if token_file_path.exists():
                with open(token_file_path, "w") as tf:
                    tf.write(creds.to_json())
        except Exception as rex:
            logger.error(f"Failed to refresh access token automatically: {rex}")
            creds = None

    if not creds:
        secret_path = Path("client_secrets.json")
        if secret_path.exists():
            logger.info("Starting local interactive web server for YouTube authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), scopes)
            creds = flow.run_local_server(port=0)
            with open(token_file_path, "w") as tf:
                tf.write(creds.to_json())
            logger.info("Successfully generated fresh session token into token.json")
        else:
            logger.warning("YouTube authentication keys are missing. Skipping deployment engine layer.")
            return None

    return build("youtube", "v3", credentials=creds)


def upload_to_cloudinary(video_path: str) -> dict:
    """Upload video to Cloudinary with auto compression."""
    try:
        logger.info("Uploading to Cloudinary with auto compression...")
        upload_result = cloudinary.uploader.upload(
            video_path,
            resource_type="video",
            folder="yt_automation",
            quality="auto",
            fetch_format="mp4",
            overwrite=True,
            invalidate=True
        )
        url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
        logger.info(f"✅ Cloudinary upload successful: {url}")
        return {"url": url, "public_id": public_id}
    except Exception as e:
        logger.error(f"Cloudinary upload error: {e}")
        return {"url": None, "public_id": None}


def generate_thumbnail_url(public_id: str) -> str:
    """Generate best-frame thumbnail from Cloudinary video."""
    try:
        thumbnail_url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            resource_type="video",
            format="jpg",
            transformation=[
                {"width": 1080, "height": 1920, "crop": "fill"},
                {"quality": "auto"},
                {"effect": "sharpen"}
            ]
        )
        logger.info(f"✅ Thumbnail URL generated: {thumbnail_url}")
        return thumbnail_url
    except Exception as e:
        logger.error(f"Thumbnail generation error: {e}")
        return None


def set_youtube_thumbnail(youtube, video_id: str, thumbnail_url: str):
    """Download thumbnail from Cloudinary and set on YouTube."""
    try:
        logger.info("Downloading thumbnail from Cloudinary for YouTube...")
        with urllib.request.urlopen(thumbnail_url) as response:
            thumbnail_data = response.read()

        logger.info("Setting thumbnail on YouTube...")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaIoBaseUpload(
                io.BytesIO(thumbnail_data),
                mimetype="image/jpeg"
            )
        ).execute()
        logger.info("✅ YouTube thumbnail set successfully!")
    except Exception as e:
        logger.error(f"YouTube thumbnail set failed: {e}")


def cleanup_cloudinary(public_id: str):
    """Delete video from Cloudinary to keep storage load 0%."""
    try:
        cloudinary.uploader.destroy(public_id, resource_type="video")
        logger.info(f"🗑️ Cloudinary Space Cleared Successfully: {public_id}")
    except Exception as e:
        logger.error(f"Cloudinary cleanup error: {e}")


def upload_all_platforms(video_path: str, seo: dict) -> dict:
    """Core pipeline gateway executing multi-platform automated deployment."""
    logger.info(f"Initiating cloud publisher engine for: {video_path}")

    title = seo.get("title", "Dark Realities Shocking Fact")
    description = seo.get("description", "A documentary discovery about human behavior.")
    hashtags = seo.get("hashtags", ["#Shorts", "#DarkPsychology", "#Mysteries"])

    if "#Shorts" not in title and "#shorts" not in title:
        title = f"{title[:50]} #Shorts"

    full_description = f"{description}\n\n" + " ".join(hashtags)
    results = {"youtube": "skipped", "facebook": "skipped", "instagram": "skipped"}

    # ------------------------------------------------
    # STEP 1: CLOUDINARY UPLOAD
    # ------------------------------------------------
    cloudinary_data = upload_to_cloudinary(video_path)
    cloudinary_url = cloudinary_data["url"]
    cloudinary_public_id = cloudinary_data["public_id"]

    if not cloudinary_url:
        logger.error("Cloudinary upload failed — aborting Meta Streams.")

    # ------------------------------------------------
    # STEP 2: GENERATE THUMBNAIL
    # ------------------------------------------------
    thumbnail_url = None
    if cloudinary_public_id:
        thumbnail_url = generate_thumbnail_url(cloudinary_public_id)

    # ------------------------------------------------
    # PHASE 1: YOUTUBE UPLOAD (AI LABEL & SPEED INDEXING ACTIVE)
    # ------------------------------------------------
    youtube = _get_youtube_service()
    if not youtube:
        logger.warning("YouTube API service initialization skipped.")
        results["youtube"] = "saved_locally_without_upload"
    else:
        try:
            body = {
                "snippet": {
                    "title": title[:100],
                    "description": full_description,
                    "tags": [tag.replace("#", "") for tag in hashtags],
                    "categoryId": "22",
                    "defaultAudioLanguage": "en-US",
                    "defaultLanguage": "en-US"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                    "selfDeclaredMadeWithAI": True
                },
                "recordingDetails": {
                    "locationDescription": "United States"
                }
            }
            media = MediaFileUpload(str(video_path), chunksize=1024 * 1024 * 2, resumable=True, mimetype="video/mp4")
            
            request = youtube.videos().insert(
                part="snippet,status,recordingDetails", 
                body=body, 
                media_body=media
            )

            logger.info(f"Uploading to YouTube: '{title}'")
            response = None
            while response is None:
                status, response = request.next_chunk()

            youtube_id = response.get('id')
            logger.info(f"✅ YouTube Upload Successful! Video ID: {youtube_id}")
            results["youtube"] = f"success_id_{youtube_id}"

            if thumbnail_url and youtube_id:
                set_youtube_thumbnail(youtube, youtube_id, thumbnail_url)

        except Exception as err:
            logger.error(f"YouTube upload failed: {err}")
            results["youtube"] = f"failed: {str(err)}"

    # ------------------------------------------------
    # PHASE 2: FACEBOOK REELS (RUNS INSTANTLY NOW)
    # ------------------------------------------------
    meta_caption = f"{title}\n\n{full_description}"

    if META_TOKEN and FB_PAGE_ID and cloudinary_url:
        fb_res = post_to_facebook_via_url(cloudinary_url, thumbnail_url, meta_caption)
        results["facebook"] = fb_res
    else:
        logger.warning("Facebook skipped.")

    # ------------------------------------------------
    # PHASE 3: INSTAGRAM REELS (RUNS INSTANTLY NOW)
    # ------------------------------------------------
    if META_TOKEN and IG_ACCT_ID and cloudinary_url:
        ig_res = post_to_instagram_via_url(cloudinary_url, meta_caption)
        results["instagram"] = ig_res
    else:
        logger.warning("Instagram skipped.")

    # ------------------------------------------------
    # STEP 3: IMMEDIATE CLEANUP (FIXED BOTTLENECK)
    # ------------------------------------------------
    if cloudinary_public_id:
        # 20 mins ka sleep hata diya hai taake GitHub script ko hang samajh kar kill na kare
        logger.info("Wiping video from Cloudinary storage instantly after Meta/YT handshakes...")
        cleanup_cloudinary(cloudinary_public_id)
    
    return results


def post_to_facebook_via_url(video_url: str, thumb_url: str, caption: str) -> str:
    try:
        url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/videos"
        payload = {
            'description': caption,
            'file_url': video_url,
            'access_token': META_TOKEN
        }
        if thumb_url:
            payload['thumb'] = thumb_url

        res = requests.post(url, data=payload, timeout=60).json()
        if "id" in res:
            logger.info(f"✅ Facebook Page Upload Successful! ID: {res['id']}")
            return f"success_id_{res['id']}"
        return f"failed: {json.dumps(res)}"
    except Exception as e:
        return f"failed_exception: {str(e)}"


def post_to_instagram_via_url(video_url: str, caption: str) -> str:
    try:
        container_url = f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media"
        payload = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption,
            'cover_frame_time': 0,
            'access_token': META_TOKEN
        }
        req = requests.post(container_url, data=payload, timeout=60)
        res_data = req.json()
        creation_id = res_data.get('id')

        if not creation_id:
            return f"failed_container_creation: {json.dumps(res_data)}"

        logger.info("Waiting 45 seconds for Instagram processing container...")
        time.sleep(45)

        publish_url = f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media_publish"
        res = requests.post(publish_url, data={'creation_id': creation_id, 'access_token': META_TOKEN}, timeout=60)
        pub_data = res.json()

        if "id" in pub_data:
            logger.info(f"✅ Instagram Reel Published! ID: {pub_data['id']}")
            return f"success_id_{pub_data['id']}"
        return f"failed_publish_error: {json.dumps(pub_data)}"
    except Exception as e:
        return f"failed_exception: {str(e)}"
