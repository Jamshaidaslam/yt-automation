import os
from pathlib import Path

# ==========================================
# 1. BASE DIRECTORIES & STORAGE SETUP
# ==========================================
BASE_DIR         = Path(__file__).resolve().parent
SCRIPTS_DIR      = BASE_DIR / "output" / "scripts"
AUDIO_DIR        = BASE_DIR / "output" / "audio"
FINAL_VIDEOS_DIR = BASE_DIR / "output" / "final_videos"
FONTS_DIR        = BASE_DIR / "fonts"
MEDIA_DIR        = BASE_DIR / "output" / "media"
VIDEO_DIR        = BASE_DIR / "output" / "media"
DOWNLOADS_DIR    = BASE_DIR / "output" / "downloads"

for d in [SCRIPTS_DIR, AUDIO_DIR, FINAL_VIDEOS_DIR, FONTS_DIR,
          MEDIA_DIR, VIDEO_DIR, DOWNLOADS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. VIDEO & AUDIO SPECIFICATIONS (9:16 Shorts)
# ==========================================
VIDEO_WIDTH  = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS    = 30

# BUG FIX 1: MEDIA_PER_KEYWORD = 3 tha — 3 keywords * 3 clips = 9 clips max.
# 9 clips * 2s fast cut = 18s video — 35s minimum duration poori nahi hoti thi.
# RuntimeError "No video clips" wahan se aata tha jab clips process hote hote
# duration cover nahi hoti thi. 8 kar diya: 3 * 8 = 24 clips = 48s coverage.
MEDIA_PER_KEYWORD  = 8

MEDIA_ORIENTATION  = "portrait"

# BUG FIX 2: MEDIA_MIN_DURATION = 3, MEDIA_MAX_DURATION = 15 tha.
# Pexels/Pixabay pe portrait orientation mein 3-15s clips bahut kam milti hain —
# zyada tar clips 16-30s ki hoti hain jo filter out ho jaati thin.
# Result: empty candidates list → zero downloads → RuntimeError.
# Min 2s tak gira diya (2s clip bhi kaam karta hai fast cuts mein),
# Max 60s kar diya taake zyada clips available hon — video_compiler
# khud subclip(0, FAST_CUT_DUR) se trim kar leta hai.
MEDIA_MIN_DURATION = 2
MEDIA_MAX_DURATION = 60

# Caption config
SUBTITLE_ANIMATION_STYLE = "pop"
CAPTION_COLOR            = "yellow"
HIGHLIGHT_COLOR          = "green"

# ==========================================
# 3. STOCK VIDEO API BASE URLS
# ==========================================
PEXELS_BASE_URL  = "https://api.pexels.com/videos/search"
PIXABAY_BASE_URL = "https://pixabay.com/api/videos/"

# ==========================================
# 4. CLOUD RETRY & TIMEOUT MECHANISMS
# ==========================================
API_RETRY_ATTEMPTS = 3
API_RETRY_WAIT_SEC = 5
API_TIMEOUT_SEC    = 30

# ==========================================
# 5. YOUTUBE AUTOMATION & BRANDING
# ==========================================
FONT_NAME      = "AmericanCaptain-MdEY.otf"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# ==========================================
# 6. API KEYS (GitHub Secrets se load hoti hain)
# ==========================================
GROQ_API_KEY    = os.environ.get("GROQ_API_KEY",    "")
PEXELS_API_KEY  = os.environ.get("PEXELS_API_KEY",  "")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")

# Startup validation — agar key missing ho toh clearly warn karo
if not GROQ_API_KEY:
    import logging
    logging.getLogger(__name__).warning("⚠️  GROQ_API_KEY not set in environment.")
if not PEXELS_API_KEY:
    import logging
    logging.getLogger(__name__).warning("⚠️  PEXELS_API_KEY not set in environment.")
if not PIXABAY_API_KEY:
    import logging
    logging.getLogger(__name__).warning("⚠️  PIXABAY_API_KEY not set in environment.")
