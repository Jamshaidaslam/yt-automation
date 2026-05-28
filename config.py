"""
config.py — Centralised Configuration
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
All API keys, folder paths, video parameters, and platform settings live here.
Every other module imports from this file so changes propagate everywhere.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env for local development (GitHub Actions uses Secrets directly) ──
load_dotenv()


# ═══════════════════════════════════════════════════════════════════════════════
# 1.  ROOT PATHS
# ═══════════════════════════════════════════════════════════════════════════════

BASE_DIR        = Path(__file__).parent.resolve()
FONTS_DIR       = BASE_DIR / "fonts"
OUTPUT_DIR      = BASE_DIR / "output"
AUDIO_DIR       = OUTPUT_DIR / "audio"
SCRIPTS_DIR     = OUTPUT_DIR / "scripts"
MEDIA_DIR       = OUTPUT_DIR / "media"
FINAL_VIDEOS_DIR = OUTPUT_DIR / "final_videos"

# Create all output subdirectories at import time
for _dir in (AUDIO_DIR, SCRIPTS_DIR, MEDIA_DIR, FINAL_VIDEOS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  API KEYS  (pulled from environment / GitHub Secrets)
# ═══════════════════════════════════════════════════════════════════════════════

GROQ_API_KEY        = os.environ["GROQ_API_KEY"]
PEXELS_API_KEY      = os.environ["PEXELS_API_KEY"]
PIXABAY_API_KEY     = os.environ["PIXABAY_API_KEY"]

# YouTube OAuth2 — the full JSON string of the client-secret file
YOUTUBE_CLIENT_SECRET_JSON = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
# YouTube OAuth2 token (serialised JSON, stored after first authorisation)
YOUTUBE_TOKEN_JSON  = os.environ.get("YOUTUBE_TOKEN_JSON", "")

# Meta Graph API — long-lived Page Access Token
META_ACCESS_TOKEN   = os.environ.get("META_ACCESS_TOKEN", "")
# Instagram Business Account ID linked to the Facebook Page
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
# Facebook Page ID for Reels posting
FACEBOOK_PAGE_ID    = os.environ.get("FACEBOOK_PAGE_ID", "")


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  GROQ / LLM SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

GROQ_MODEL          = "llama3-70b-8192"   # Switch to "llama3-8b-8192" if quota is tight
GROQ_MAX_TOKENS     = 1024
GROQ_TEMPERATURE    = 0.85

# Topic & audience hint injected into every system prompt
NICHE_CONTEXT = (
    "AI and Dark Realities — deep, suspenseful, psychological, and analytical facts "
    "about artificial intelligence, surveillance, algorithmic manipulation, and the "
    "hidden costs of technology. Target audience: curious adults aged 18-45 in the USA "
    "and UK who enjoy mind-bending, thought-provoking short-form content."
)


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  VIDEO PARAMETERS
# ═══════════════════════════════════════════════════════════════════════════════

VIDEO_WIDTH         = 1080          # Strict 9:16 vertical canvas
VIDEO_HEIGHT        = 1920
VIDEO_FPS           = 30
VIDEO_BITRATE       = "4000k"       # Enough for 1080p vertical; keeps file size sane
AUDIO_BITRATE       = "192k"
MIN_DURATION_SEC    = 30            # Script generation target
MAX_DURATION_SEC    = 59

# Clip cutting rhythm (seconds per B-roll clip) — keeps energy high
CLIP_MIN_SEC        = 2.0
CLIP_MAX_SEC        = 3.0

# Motion effect intensity (zoom factor added per clip)
ZOOM_FACTOR         = 0.04          # 4% zoom over the full clip duration
PAN_SPEED           = 0.015         # Pixel fraction per frame for slow-pan

# Background fill colour when a clip doesn't fully cover the canvas
BG_COLOR            = (0, 0, 0)     # Pure black


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  CAPTION / FONT SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Place your font file (e.g. Montserrat-ExtraBold.ttf) inside ./fonts/
FONT_FILE           = str(FONTS_DIR / "Montserrat-ExtraBold.ttf")

# Active-word highlight colour (word currently being spoken)
CAPTION_ACTIVE_COLOR    = "#00FF00"   # Electric green — change to "#FFFF00" for yellow
# Inactive words shown simultaneously (recent context)
CAPTION_INACTIVE_COLOR  = "#FFFFFF"
CAPTION_OUTLINE_COLOR   = "#000000"  # Hard outline behind every word

CAPTION_FONT_SIZE       = 72         # px — large enough for mobile screens
CAPTION_OUTLINE_WIDTH   = 6          # px stroke around each letter
CAPTION_Y_FRACTION      = 0.68       # Vertical position: 68% down the frame (lower-middle third)
CAPTION_MAX_CHARS_LINE  = 22         # Wrap caption line at this character count
CAPTION_WORDS_VISIBLE   = 4          # How many words to show simultaneously on screen


# ═══════════════════════════════════════════════════════════════════════════════
# 6.  TTS SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

TTS_VOICE           = "en-US-ChristopherNeural"   # Deep, authoritative male voice
# Alternatives: "en-US-BrianNeural", "en-GB-RyanNeural"
TTS_RATE            = "-5%"          # Slightly slower for gravitas
TTS_VOLUME          = "+0%"


# ═══════════════════════════════════════════════════════════════════════════════
# 7.  MEDIA SEARCH SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

PEXELS_BASE_URL     = "https://api.pexels.com/videos/search"
PIXABAY_BASE_URL    = "https://pixabay.com/api/videos/"
MEDIA_PER_KEYWORD   = 3             # Clips fetched per keyword (before dedup)
MEDIA_MIN_DURATION  = 5             # Only accept clips ≥ 5 s from APIs
MEDIA_MAX_DURATION  = 30            # Skip very long clips to reduce download size
MEDIA_ORIENTATION   = "portrait"    # Prefer vertical clips natively


# ═══════════════════════════════════════════════════════════════════════════════
# 8.  YOUTUBE UPLOAD DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════

YT_CATEGORY_ID      = "28"          # Science & Technology
YT_PRIVACY_STATUS   = "public"
YT_MADE_FOR_KIDS    = False


# ═══════════════════════════════════════════════════════════════════════════════
# 9.  META GRAPH API SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

META_API_VERSION    = "v20.0"
META_BASE_URL       = f"https://graph.facebook.com/{META_API_VERSION}"


# ═══════════════════════════════════════════════════════════════════════════════
# 10.  RETRY / RESILIENCE
# ═══════════════════════════════════════════════════════════════════════════════

API_RETRY_ATTEMPTS  = 3
API_RETRY_WAIT_SEC  = 5
