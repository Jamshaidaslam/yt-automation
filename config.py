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

# Automatic directory creation taake FileNotFoundError na aaye
for d in [SCRIPTS_DIR, AUDIO_DIR, FINAL_VIDEOS_DIR, FONTS_DIR]:
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
SUBTITLE_ANIMATION_STYLE = "pop"  # fast-cutting text pop effect
CAPTION_COLOR = "yellow"          # Accessibility matching branding
HIGHLIGHT_COLOR = "green"         # High-retention text highlights

# ==========================================
# 3. STOCK VIDEO API BASE URLS
# ==========================================
PEXELS_BASE_URL = "https://api.pexels.com/videos/"
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
FONT_NAME = "Impact.ttf"  # Fallback font name

# STRICT YOUTUBE OAUTH SCOPES (Fixes bad request invalid_scope)
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# ==========================================
# 6. SECURE API KEYS CONFIGURATION (GitHub Secrets)
# ==========================================
# Yeh structure cloud environments aur local donon ke liye 100% safe hai
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_KEY_HERE")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "YOUR_PEXELS_KEY_HERE")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "YOUR_PIXABAY_KEY_HERE")
