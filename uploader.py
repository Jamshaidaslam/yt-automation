"""
uploader.py — Secure Channel Publisher Engine (FIXED FOR DARK PSYCHOLOGY & AUTO-REFRESH)
AI Dark Realities · Short-Form Video Pipeline
─────────────────────────────────────────────────────────────────────────────────────
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
    Authenticates and constructs the YouTube API service with auto-refresh layers.
    """
    creds = None
    scopes = getattr(config, "YOUTUBE_SCOPES", ["https://www.googleapis.com/auth/youtube.upload"])
    
    # 1. GitHub Actions Cloud Secrets checking layer
    if os.environ.get("YOUTUBE_TOKEN_JSON"):
        try:
            token_data = json.loads(os.environ.get("YOUTUBE_TOKEN_JSON"))
            creds = Credentials.from_authorized_user_info(token_data, scopes)
        except Exception as exc:
            logger.warning(f"Cloud credentials parsing failed: {exc}")

    # 2. Local token file checking layer (For initial login generation)
    token_file_path = Path("token.json")
    if not creds and token_file_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file_path), scopes)
        except Exception as exc:
            logger.warning(f"Local token file parsing failed: {exc}")

    # 3. CRITICAL FIX: Auto-Refresh expired sessions silently
    if creds and creds.expired and creds.refresh_token:
        try:
            logger.info("YouTube session expired. Attemping background auto-refresh...")
            creds.refresh(Request())
            # Dynamically update the token file if running locally
            if token_file_path.exists():
                with open(token_file_path, "w") as tf:
                    tf.write(creds.to_json())
        except Exception as rex:
            logger.error(f"Failed to refresh access token automatically: {rex}")
            creds = None

    # 4. Fallback authentication trigger (Only runs interactively on your laptop)
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

def upload_all_platforms(video_path: str, seo: dict) -> dict:
    """
    Core pipeline gateway executing multi-platform automated deployment.
    """
    logger.info(f"Initiating cloud publisher engine for: {video_path}")
    
    title = seo.get("title", "Dark Realities Shocking Fact")
    description = seo.get("description", "A documentary discovery about human behavior.")
    hashtags = seo.get("hashtags", ["#Shorts", "#DarkPsychology", "#Mysteries"])
    
    # Algo optimization: Append #Shorts to title explicitly
    if "#Shorts" not in title and "#shorts" not in title:
        title = f"{title[:50]} #Shorts"
        
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
                "tags": [tag.replace("#", "") for tag in hashtags],
                "categoryId": "24"  # 🟢 Entertainment category (Perfect for Dark Psychology/Mysteries)
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        # 🟢 FIXED: Using stable 2MB buffer blocks to prevent GitHub Actions stream dropouts
        media = MediaFileUpload(str(video_path), chunksize=1024 * 1024 * 2, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        logger.info(f"Uploading short form video to YouTube Channel: '{title}'")
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"YouTube Upload Progress: {int(status.progress() * 100)}%")
                
        logger.info(f"✅ YouTube Upload Successful! Video ID: {response.get('id')}")
        results["youtube"] = f"success_id_{response.get('id')}"
    except Exception as err:
        logger.error(f"YouTube upload failed with API exception: {err}")
        results["youtube"] = f"failed: {str(err)}"
        
    return results
