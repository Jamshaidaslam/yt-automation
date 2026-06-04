import os
from pathlib import Path

# ==========================================
# 1. BASE DIRECTORIES & STORAGE SETUP
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "output" / "scripts"
AUDIO_DIR = BASE_DIR / "output" / "audio"
FINAL_VIDEOS_DIR = BASE_DIR / "output" / "final_videos"
FONTS_DIR = BASE_DIR / "fonts"

MEDIA_DIR = BASE_DIR / "output" / "media"
VIDEO_DIR = BASE_DIR / "output" / "media"

# FIX: DOWNLOADS_DIR was missing — media_fetcher.py was crashing with AttributeError
DOWNLOADS_DIR = BASE_DIR / "output" / "downloads"

for d in [SCRIPTS_DIR, AUDIO_DIR, FINAL_VIDEOS_DIR, FONTS_DIR, MEDIA_DIR, VIDEO_DIR, DOWNLOADS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. VIDEO & AUDIO SPECIFICATIONS (9:16 Shorts)
# ==========================================
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Media Fetching Engine Parameters
MEDIA_PER_KEYWORD = 3
MEDIA_ORIENTATION = "portrait"
MEDIA_MIN_DURATION = 3
MEDIA_MAX_DURATION = 15

# Subtitle & Caption Animations Configuration
SUBTITLE_ANIMATION_STYLE = "pop"
CAPTION_COLOR = "yellow"
HIGHLIGHT_COLOR = "green"

# ==========================================
# 3. STOCK VIDEO API BASE URLS
# FIX: Pexels URL was missing /search — correct endpoint is /videos/search
# ==========================================
PEXELS_BASE_URL = "https://api.pexels.com/videos/search"
PIXABAY_BASE_URL = "https://pixabay.com/api/videos/"

# ==========================================
# 4. CLOUD RETRY & TIMEOUT MECHANISMS
# ==========================================
API_RETRY_ATTEMPTS = 3
API_RETRY_WAIT_SEC = 5
API_TIMEOUT_SEC = 30

# ==========================================
# 5. YOUTUBE AUTOMATION & BRANDING FALLBACKS
# ==========================================
FONT_NAME = "AmericanCaptain-MdEY.otf"

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# ==========================================
# 6. SECURE API KEYS CONFIGURATION (GitHub Secrets)
# ==========================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_KEY_HERE")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "YOUR_PEXELS_KEY_HERE")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "YOUR_PIXABAY_KEY_HERE")
