"""
uploader.py — Multi-Platform Video Uploader
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
Handles automated posting to:
  • YouTube Shorts  — via YouTube Data API v3 (OAuth2)
  • Instagram Reels — via Meta Graph API (Page Access Token)
  • Facebook Reels  — via Meta Graph API (Page Access Token)
  • Snapchat        — Folder drop + structured upload-ready output
                      (Snapchat Spotlight API requires business approval;
                       this module writes the required metadata sidecar)

All uploads are retried up to config.API_RETRY_ATTEMPTS times.
"""

import json
import logging
import mimetypes
import os
import time
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# ═══════════════════════════════════════════════════════════════════════════════
# 1.  YOUTUBE SHORTS UPLOADER
# ═══════════════════════════════════════════════════════════════════════════════

def _get_youtube_service():
    """
    Build an authenticated YouTube Data API v3 service object.

    Flow:
      • In CI (GitHub Actions): YOUTUBE_TOKEN_JSON secret holds a pre-authorised
        OAuth2 token JSON.  No browser interaction required.
      • Local first-run: if token is absent, initiate device-flow authorisation
        and persist the resulting token as YOUTUBE_TOKEN_JSON.
    """
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import google_auth_oauthlib.flow as oauthflow

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    creds  = None

    # ── Try to load existing token ───────────────────────────────────────────
    token_json = config.YOUTUBE_TOKEN_JSON
    if token_json:
        try:
            token_data = json.loads(token_json)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as exc:
            logger.warning(f"Could not parse YOUTUBE_TOKEN_JSON: {exc}")

    # ── Refresh expired token ────────────────────────────────────────────────
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            logger.info("YouTube OAuth2 token refreshed successfully.")
        except Exception as exc:
            logger.error(f"Token refresh failed: {exc}")
            creds = None

    # ── First-time local authorisation (not used in CI) ──────────────────────
    if not creds or not creds.valid:
        secret_json = config.YOUTUBE_CLIENT_SECRET_JSON
        if not secret_json:
            raise RuntimeError(
                "YOUTUBE_CLIENT_SECRET env var is empty. "
                "Store your OAuth2 client secret JSON in this variable."
            )
        # Write temp file for the oauthlib flow
        tmp_secret = Path("/tmp/yt_client_secret.json")
        tmp_secret.write_text(secret_json)
        flow = oauthflow.InstalledAppFlow.from_client_secrets_file(
            str(tmp_secret), SCOPES
        )
        creds = flow.run_local_server(port=0)
        logger.info(
            "New YouTube token obtained. Store this as YOUTUBE_TOKEN_JSON:\n"
            + creds.to_json()
        )

    return build("youtube", "v3", credentials=creds, cache_discovery=False)


@retry(stop=stop_after_attempt(config.API_RETRY_ATTEMPTS),
       wait=wait_fixed(config.API_RETRY_WAIT_SEC))
def upload_to_youtube(video_path: str, seo: dict) -> str:
    """
    Upload a video to YouTube as a Short.

    Parameters
    ----------
    video_path : str  — path to the final MP4 file
    seo        : dict — {title, description, hashtags}

    Returns
    -------
    str — YouTube video ID
    """
    from googleapiclient.http import MediaFileUpload

    logger.info(f"Uploading to YouTube: {Path(video_path).name}")

    youtube = _get_youtube_service()

    # Build description with inline hashtags
    hashtag_str  = " ".join(seo.get("hashtags", []))
    description  = f"{seo.get('description', '')}\n\n{hashtag_str}\n\n#Shorts"

    body = {
        "snippet": {
            "title":       seo["title"][:100],   # YouTube max = 100 chars
            "description": description[:5000],    # YouTube max = 5000 chars
            "tags":        seo.get("hashtags", []),
            "categoryId":  config.YT_CATEGORY_ID,
        },
        "status": {
            "privacyStatus":         config.YT_PRIVACY_STATUS,
            "selfDeclaredMadeForKids": config.YT_MADE_FOR_KIDS,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype    = "video/mp4",
        resumable   = True,
        chunksize   = 5 * 1024 * 1024,   # 5 MB chunks
    )

    request = youtube.videos().insert(
        part  = "snippet,status",
        body  = body,
        media_body = media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info(f"YouTube upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id", "UNKNOWN")
    logger.info(f"✅ YouTube upload complete. Video ID: {video_id}")
    logger.info(f"   URL: https://www.youtube.com/shorts/{video_id}")
    return video_id


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  META GRAPH API  (Instagram Reels + Facebook Reels)
# ═══════════════════════════════════════════════════════════════════════════════

def _meta_request(method: str, endpoint: str, **kwargs) -> dict:
    """Thin wrapper around requests for Meta Graph API calls."""
    url  = f"{config.META_BASE_URL}/{endpoint}"
    resp = requests.request(method, url, timeout=120, **kwargs)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"Meta API error: {data['error']}")
    return data


@retry(stop=stop_after_attempt(config.API_RETRY_ATTEMPTS),
       wait=wait_fixed(10))
def upload_to_instagram_reels(video_path: str, seo: dict) -> str:
    """
    Upload a Reel to Instagram using the Meta Graph API.

    Step 1: Create a media container (upload video URL required — use a
            publicly accessible URL).  Since our video is local we first
            upload via the resumable endpoint and then finalise.

    NOTE: Meta requires the video to be served from a publicly reachable URL
    OR uploaded via the resumable upload endpoint.  This implementation uses
    the resumable upload endpoint available for Instagram Graph API.

    Returns the Instagram media ID.
    """
    logger.info(f"Uploading to Instagram Reels: {Path(video_path).name}")
    token        = config.META_ACCESS_TOKEN
    account_id   = config.INSTAGRAM_ACCOUNT_ID
    hashtag_str  = " ".join(seo.get("hashtags", []))
    caption      = f"{seo['title']}\n\n{seo.get('description', '')}\n\n{hashtag_str}"[:2200]

    # ── Step 1: Initialise resumable upload session ──────────────────────────
    file_size = os.path.getsize(video_path)
    init_resp = _meta_request(
        "POST",
        f"{account_id}/video_reels",
        params={
            "upload_type":    "resumable",
            "access_token":   token,
        },
        json={
            "upload_phase": "start",
            "file_size":    file_size,
        }
    )
    video_id    = init_resp["video_id"]
    upload_url  = init_resp["upload_url"]
    logger.info(f"Instagram container created. video_id={video_id}")

    # ── Step 2: Upload video bytes ───────────────────────────────────────────
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_resp = requests.post(
        upload_url,
        headers={
            "Authorization":    f"OAuth {token}",
            "offset":           "0",
            "file_size":        str(file_size),
        },
        data=video_bytes,
        timeout=300,
    )
    upload_resp.raise_for_status()
    logger.info("Instagram video bytes uploaded.")

    # ── Step 3: Publish the Reel ─────────────────────────────────────────────
    publish_resp = _meta_request(
        "POST",
        f"{account_id}/video_reels",
        params={"access_token": token},
        json={
            "upload_phase":    "finish",
            "video_id":        video_id,
            "caption":         caption,
            "video_state":     "PUBLISHED",
            "share_to_feed":   True,
        }
    )
    media_id = publish_resp.get("id", video_id)
    logger.info(f"✅ Instagram Reel published. Media ID: {media_id}")
    return media_id


@retry(stop=stop_after_attempt(config.API_RETRY_ATTEMPTS),
       wait=wait_fixed(10))
def upload_to_facebook_reels(video_path: str, seo: dict) -> str:
    """
    Upload a Reel to a Facebook Page using the Meta Graph API.

    Three-step process:
      1. Initialise a video upload session on the Page.
      2. Transfer the video bytes via the upload URL.
      3. Publish the Reel.

    Returns the Facebook video ID.
    """
    logger.info(f"Uploading to Facebook Reels: {Path(video_path).name}")
    token     = config.META_ACCESS_TOKEN
    page_id   = config.FACEBOOK_PAGE_ID
    hashtag_str = " ".join(seo.get("hashtags", []))
    description = f"{seo['title']}\n\n{seo.get('description', '')}\n\n{hashtag_str}"[:63206]

    file_size = os.path.getsize(video_path)

    # ── Step 1: Initialise upload ────────────────────────────────────────────
    init_data = _meta_request(
        "POST",
        f"{page_id}/video_reels",
        params={"access_token": token},
        json={
            "upload_phase": "start",
            "file_size":    file_size,
        }
    )
    video_id   = init_data["video_id"]
    upload_url = init_data["upload_url"]
    logger.info(f"Facebook upload session started. video_id={video_id}")

    # ── Step 2: Upload bytes ─────────────────────────────────────────────────
    with open(video_path, "rb") as f:
        upload_resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {token}",
                "offset":        "0",
                "file_size":     str(file_size),
            },
            data=f,
            timeout=300,
        )
    upload_resp.raise_for_status()
    logger.info("Facebook video bytes transferred.")

    # ── Step 3: Publish ──────────────────────────────────────────────────────
    publish_data = _meta_request(
        "POST",
        f"{page_id}/video_reels",
        params={"access_token": token},
        json={
            "upload_phase":  "finish",
            "video_id":      video_id,
            "video_state":   "PUBLISHED",
            "description":   description,
        }
    )
    fb_id = publish_data.get("id", video_id)
    logger.info(f"✅ Facebook Reel published. Video ID: {fb_id}")
    return fb_id


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  SNAPCHAT — Metadata Sidecar Output
# ═══════════════════════════════════════════════════════════════════════════════

def prepare_snapchat_output(video_path: str, seo: dict) -> str:
    """
    Snapchat Spotlight upload via API requires business-level API approval.
    This function writes a metadata JSON sidecar alongside the video file so
    the video is ready for manual upload or a future webhook integration.

    Returns path to the metadata JSON file.
    """
    video_path  = Path(video_path)
    meta_path   = video_path.with_suffix(".snapchat_meta.json")
    hashtag_str = " ".join(seo.get("hashtags", []))

    metadata = {
        "title":          seo["title"],
        "caption":        f"{seo.get('description', '')}\n\n{hashtag_str}"[:150],
        "is_spotlight":   True,
        "video_path":     str(video_path.resolve()),
        "topics":         ["AI", "Technology", "Dark Realities", "Education"],
        "ready_to_upload": True,
    }

    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info(f"Snapchat metadata sidecar written → {meta_path.name}")
    return str(meta_path)


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  ORCHESTRATOR — upload to all platforms
# ═══════════════════════════════════════════════════════════════════════════════

def upload_all_platforms(video_path: str, seo: dict) -> dict:
    """
    Attempt upload to all configured platforms.
    Returns a dict of {platform: result_or_error_string}.
    Never raises — all failures are captured and returned.
    """
    results = {}

    # ── YouTube ──────────────────────────────────────────────────────────────
    try:
        yt_id = upload_to_youtube(video_path, seo)
        results["youtube"] = {"status": "success", "id": yt_id}
    except Exception as exc:
        logger.error(f"YouTube upload failed: {exc}")
        results["youtube"] = {"status": "error", "message": str(exc)}

    # ── Instagram Reels ──────────────────────────────────────────────────────
    if config.INSTAGRAM_ACCOUNT_ID and config.META_ACCESS_TOKEN:
        try:
            ig_id = upload_to_instagram_reels(video_path, seo)
            results["instagram"] = {"status": "success", "id": ig_id}
        except Exception as exc:
            logger.error(f"Instagram upload failed: {exc}")
            results["instagram"] = {"status": "error", "message": str(exc)}
    else:
        logger.warning("Instagram upload skipped — INSTAGRAM_ACCOUNT_ID or META_ACCESS_TOKEN not set.")
        results["instagram"] = {"status": "skipped"}

    # ── Facebook Reels ───────────────────────────────────────────────────────
    if config.FACEBOOK_PAGE_ID and config.META_ACCESS_TOKEN:
        try:
            fb_id = upload_to_facebook_reels(video_path, seo)
            results["facebook"] = {"status": "success", "id": fb_id}
        except Exception as exc:
            logger.error(f"Facebook upload failed: {exc}")
            results["facebook"] = {"status": "error", "message": str(exc)}
    else:
        logger.warning("Facebook upload skipped — FACEBOOK_PAGE_ID or META_ACCESS_TOKEN not set.")
        results["facebook"] = {"status": "skipped"}

    # ── Snapchat ─────────────────────────────────────────────────────────────
    try:
        snap_meta = prepare_snapchat_output(video_path, seo)
        results["snapchat"] = {"status": "ready", "meta_file": snap_meta}
    except Exception as exc:
        logger.error(f"Snapchat metadata failed: {exc}")
        results["snapchat"] = {"status": "error", "message": str(exc)}

    # ── Summary ──────────────────────────────────────────────────────────────
    logger.info("Upload results:")
    for platform, result in results.items():
        logger.info(f"  {platform:12s}: {result}")

    return results
