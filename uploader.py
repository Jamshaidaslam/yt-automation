"""
uploader.py — Secure Channel Publisher Engine (FINAL - FB DISABLED, INSTA FIXED)
AI Dark Realities · Short-Form Video Pipeline
─────────────────────────────────────────────────────────────────────────────────────
"""

import json
import logging
import os
import time
import requests
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

META_TOKEN = os.environ.get("META_ACCESS_TOKEN")
IG_ACCT_ID = os.environ.get("INSTAGRAM_BUSINESS_ID")

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


def upload_all_platforms(video_path: str, seo: dict) -> dict:
    logger.info(f"Initiating cloud publisher engine for: {video_path}")
    
    title = seo.get("title", "Dark Realities Shocking Fact")
    description = seo.get("description", "A documentary discovery about human behavior.")
    hashtags = seo.get("hashtags", ["#Shorts", "#DarkPsychology", "#Mysteries"])
    
    if "#Shorts" not in title and "#shorts" not in title:
        title = f"{title[:50]} #Shorts"
        
    full_description = f"{description}\n\n" + " ".join(hashtags)
    results = {"youtube": "skipped", "facebook": "disabled", "instagram": "skipped"}
    
    # PHASE 1: YOUTUBE
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
                    "categoryId": "22"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                    "selfDeclaredMadeWithAI": True
                }
            }
            media = MediaFileUpload(str(video_path), chunksize=1024 * 1024 * 2, resumable=True, mimetype="video/mp4")
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            
            logger.info(f"Uploading to YouTube: '{title}'")
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"YouTube Upload Progress: {int(status.progress() * 100)}%")
                    
            youtube_id = response.get('id')
            logger.info(f"✅ YouTube Upload Successful! Video ID: {youtube_id}")
            results["youtube"] = f"success_id_{youtube_id}"

        except Exception as err:
            logger.error(f"YouTube upload failed: {err}")
            results["youtube"] = f"failed: {str(err)}"

    # PHASE 2: FACEBOOK — DISABLED
    logger.info("Facebook upload skipped — pending Meta app permissions fix.")
    results["facebook"] = "disabled_pending_fix"

    # PHASE 3: INSTAGRAM
    meta_caption = f"{title}\n\n{full_description}"

    if META_TOKEN and IG_ACCT_ID:
        logger.info("Generating temporary URL for Instagram ingestion...")
        temp_url = generate_temporary_url(video_path)
        if temp_url:
            logger.info(f"Temporary URL ready: {temp_url}")
            ig_res = post_to_instagram_via_url(temp_url, meta_caption)
            results["instagram"] = ig_res
        else:
            results["instagram"] = "failed_temp_url_generation"
    else:
        logger.warning("Instagram skipped: Missing META_ACCESS_TOKEN or INSTAGRAM_BUSINESS_ID.")

    return results


def generate_temporary_url(video_path: str) -> str:
    try:
        url = "https://file.io/?expires=1h"
        with open(video_path, 'rb') as video_file:
            files = {'file': video_file}
            response = requests.post(url, files=files, timeout=120)
        data = response.json()
        if data.get('success'):
            link = data.get('link')
            logger.info(f"file.io URL generated: {link}")
            return link
        logger.error(f"file.io upload failed: {data}")
        return None
    except Exception as e:
        logger.error(f"Error generating temporary URL: {e}")
        return None


def post_to_instagram_via_url(video_url: str, caption: str) -> str:
    try:
        container_url = f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media"
        payload = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption,
            'access_token': META_TOKEN
        }
        req = requests.post(container_url, data=payload, timeout=60)
        res_data = req.json()
        creation_id = res_data.get('id')

        if not creation_id:
            logger.error(f"Instagram container creation failed: {res_data}")
            return f"failed_container_creation: {json.dumps(res_data)}"

        logger.info("Waiting 60 seconds for Instagram to process video...")
        time.sleep(60)

        publish_url = f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media_publish"
        res = requests.post(
            publish_url,
            data={'creation_id': creation_id, 'access_token': META_TOKEN},
            timeout=60
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
