"""
uploader.py — Secure Channel Publisher Engine (FINAL - DELAY + STATUS CHECK FIXED)
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
    try:
        cloudinary.uploader.
