"""
uploader.py — Secure Channel Publisher Engine (FIXED FOR DIRECT BINARY UPLOAD & DEVELOPMENT MODE BYPASS)
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

# ─────────────────────────────────────────────────────────────────────────────────────
# CRITICAL FIX: GitHub Environment Secrets Mapping (Matched exactly with GitHub Secrets)
# ─────────────────────────────────────────────────────────────────────────────────────
META_TOKEN = os.environ.get("META_ACCESS_TOKEN")
FB_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
IG_ACCT_ID = os.environ.get("INSTAGRAM_BUSINESS_ID")  # Fixed variable name mapping

def _get_youtube_service():
    """Authenticates and constructs the YouTube API service with auto-refresh layers."""
    creds = None
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    
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

    # 3. Auto-Refresh expired sessions silently
    if creds and creds.expired and creds.refresh_token:
        try:
            logger.info("YouTube session expired. Attemping background auto-refresh...")
            creds.refresh(Request())
            if token_file_path.exists():
                with open(token_file_path, "w") as tf:
                    tf.write(creds.to_json())
        except Exception as rex:
            logger.error(f"Failed to refresh access token automatically: {rex}")
            creds = None

    # 4. Fallback authentication trigger
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
    """Core pipeline gateway executing multi-platform automated deployment."""
    logger.info(f"Initiating cloud publisher engine for: {video_path}")
    
    title = seo.get("title", "Dark Realities Shocking Fact")
    description = seo.get("description", "A documentary discovery about human behavior.")
    hashtags = seo.get("hashtags", ["#Shorts", "#DarkPsychology", "#Mysteries"])
    
    # Algo optimization: Append #Shorts to title explicitly
    if "#Shorts" not in title and "#shorts" not in title:
        title = f"{title[:50]} #Shorts"
        
    full_description = f"{description}\n\n" + " ".join(hashtags)
    results = {"youtube": "skipped", "facebook": "skipped", "instagram": "skipped"}
    
    # ----------------------------------------------------
    # PHASE 1: YOUTUBE DEPLOYMENT
    # ----------------------------------------------------
    youtube = _get_youtube_service()
    youtube_id = None
    
    if not youtube:
        logger.warning("YouTube API service initialization skipped (No tokens found). Video saved locally.")
        results["youtube"] = "saved_locally_without_upload"
    else:
        try:
            body = {
                "snippet": {
                    "title": title[:100],
                    "description": full_description,
                    "tags": [tag.replace("#", "") for tag in hashtags],
                    "categoryId": "24"  # Entertainment category
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }
            
            media = MediaFileUpload(str(video_path), chunksize=1024 * 1024 * 2, resumable=True, mimetype="video/mp4")
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            
            logger.info(f"Uploading short form video to YouTube Channel: '{title}'")
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"YouTube Upload Progress: {int(status.progress() * 100)}%")
                    
            youtube_id = response.get('id')
            logger.info(f"✅ YouTube Upload Successful! Video ID: {youtube_id}")
            results["youtube"] = f"success_id_{youtube_id}"
        except Exception as err:
            logger.error(f"YouTube upload failed with API exception: {err}")
            results["youtube"] = f"failed: {str(err)}"

    # ----------------------------------------------------
    # PHASE 2: META AUTOMATION LAYER (DIRECT BINARY & COMPATIBLE STREAMS)
    # ----------------------------------------------------
    meta_caption = f"{title}\n\n{full_description}"

    # 1. Facebook Page Publisher (DIRECT FILE CHUNK UPLOAD - NO URL REQUIRED)
    if META_TOKEN and FB_PAGE_ID:
        logger.info("Initiating Facebook Page Direct Binary Upload engine...")
        fb_res = post_to_facebook_direct(str(video_path), meta_caption)
        results["facebook"] = fb_res
    else:
        logger.warning("Facebook automation skipped: Missing token or Page ID secrets.")

    # 2. Instagram Reels Publisher (Requires Clean Ingestion URL Wrapper)
    if META_TOKEN and IG_ACCT_ID and youtube_id:
        logger.info("Initiating Instagram Business publishing sequence...")
        stream_clean_url = f"https://www.youtube.com/watch?v={youtube_id}"
        ig_res = post_to_instagram(stream_clean_url, meta_caption)
        results["instagram"] = ig_res
    else:
        logger.warning("Instagram automation skipped: Missing secrets or source YouTube ID.")

    return results

def post_to_facebook_direct(video_path: str, caption: str) -> str:
    """Uploads the local video file binary directly to Facebook Page via secure chunks to bypass App limits."""
    try:
        file_size = os.path.getsize(video_path)
        url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/videos"
        
        # Step A: Initialize Resumable Session
        init_payload = {'upload_phase': 'start', 'access_token': META_TOKEN, 'file_size': file_size}
        init_res = requests.post(url, data=init_payload).json()
        session_id = init_res.get('upload_session_id')
        
        if not session_id:
            logger.error(f"Facebook Chunk init failed: {init_res}")
            return f"failed_init: {json.dumps(init_res)}"
            
        # Step B: Transfer Binary Data Chunks
        with open(video_path, 'rb') as f:
            upload_payload = {
                'upload_phase': 'transfer', 'start_offset': '0',
                'upload_session_id': session_id, 'access_token': META_TOKEN
            }
            requests.post(url, data=upload_payload, files={'video_file_chunk': f})

        # Step C: Close Session & Publish to Feed
        finish_payload = {
            'upload_phase': 'finish', 'upload_session_id': session_id,
            'access_token': META_TOKEN, 'description': caption, 'title': caption[:30]
        }
        finish_res = requests.post(url, data=finish_payload).json()
        
        if finish_res.get('success') or "id" in finish_res:
            logger.info("✅ Facebook Page Direct File Upload Successful!")
            return f"success_id_{finish_res.get('id', 'published')}"
        
        logger.error(f"Facebook Chunk finish failed: {finish_res}")
        return f"failed_finish: {json.dumps(finish_res)}"
    except Exception as e:
        logger.error(f"Facebook direct upload exception: {e}")
        return f"failed_exception: {str(e)}"

def post_to_instagram(video_url: str, caption: str) -> str:
    """Injects and publishes the video directly as an Instagram Reel using stream embed wrapping."""
    try:
        container_url = f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media"
        # Bypassing raw watch links by mapping clean embed streams for development graphs
        embed_url = video_url.replace("watch?v=", "embed/")
        payload = {
            'media_type': 'REELS',
            'video_url': embed_url,
            'caption': caption,
            'access_token': META_TOKEN
        }
        req = requests.post(container_url, data=payload)
        res_data = req.json()
        creation_id = res_data.get('id')

        if not creation_id:
            logger.error(f"Instagram container creation rejected: {res_data}")
            return f"failed_container_creation: {json.dumps(res_data)}"

        logger.info("Instagram ingestion active. Sleeping 45 seconds for cloud processing...")
        time.sleep(45)

        publish_url = f"https://graph.facebook.com/v20.0/{IG_ACCT_ID}/media_publish"
        res = requests.post(publish_url, data={'creation_id': creation_id, 'access_token': META_TOKEN})
        pub_data = res.json()

        if "id" in pub_data:
            logger.info(f"✅ Instagram Reel Publish Successful! ID: {pub_data['id']}")
            return f"success_id_{pub_data['id']}"
        else:
            logger.error(f"Instagram feed dispatch engine error: {pub_data}")
            return f"failed_publish_error: {json.dumps(pub_data)}"

    except Exception as e:
        logger.error(f"Instagram request execution failure: {e}")
        return f"failed_exception: {str(e)}"
