"""
uploader.py — Secure Channel Publisher Engine
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import json
import logging
import os
from pathlib import Path
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

def _get_youtube_service():
    """
    Authenticates and constructs the YouTube API service.
    """
    creds = None
    # GitHub Actions environment friendly configuration
    scopes = getattr(config, "YOUTUBE_SCOPES", ["https://www.googleapis.com/auth/youtube.upload"])
    
    # Cloud automatic bypass layer
    if os.environ.get("YOUTUBE_TOKEN_JSON"):
        try:
            token_data = json.loads(os.environ.get("YOUTUBE_TOKEN_JSON"))
            creds = Credentials.from_authorized_user_info(token_data, scopes)
        except Exception as exc:
            logger.warning(f"Cloud credentials parsing failed: {exc}")

    if not creds:
        logger.warning("YouTube environment credentials missing. Skipping authentications.")
        return None
        
    return build("youtube", "v3", credentials=creds)

def upload_all_platforms(video_path: str, seo: dict) -> dict:
    """
    CRITICAL FIX: This function was missing and causing AttributeError in main.py.
    """
    logger.info(f"Initiating cloud publisher engine for: {video_path}")
    title = seo.get("title", "Dark Realities Shocking Fact")
    description = seo.get("description", "A documentary discovery about technology.")
    hashtags = seo.get("hashtags", ["#Shorts", "#DarkReality"])
    
    full_description = f"{description}\n\n" + " ".join(hashtags)
    results = {"youtube": "skipped"}
    
    youtube = _get_youtube_service()
    if not youtube:
        logger.warning("YouTube API service initialization skipped (No tokens found). Video saved locally.")
        return {"youtube": "saved_locally_without_upload"}
        
    try:
        body = {
            "snippet": {
                "title": title[:100],
                "description": full_description,
                "categoryId": "28"  # Science & Technology
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        logger.info(f"Uploading short form draft to YouTube: '{title}'")
        response = request.execute()
        logger.info(f"YouTube Upload Successful! Video ID: {response.get('id')}")
        results["youtube"] = f"success_id_{response.get('id')}"
    except Exception as err:
        logger.error(f"YouTube upload failed with API exception: {err}")
        results["youtube"] = f"failed: {str(err)}"
        
    return results
