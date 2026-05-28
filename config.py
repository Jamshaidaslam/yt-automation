import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "output" / "scripts"
AUDIO_DIR = BASE_DIR / "output" / "audio"
FINAL_VIDEOS_DIR = BASE_DIR / "output" / "final_videos"
FONTS_DIR = BASE_DIR / "fonts"

for d in [SCRIPTS_DIR, AUDIO_DIR, FINAL_VIDEOS_DIR, FONTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Video Specs (9:16 Vertical Video for Shorts/Reels)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
MEDIA_PER_KEYWORD = 3
MEDIA_ORIENTATION = "portrait"  # Fixes Pexels orientation missing error

# API Settings & Base URLs
API_RETRY_ATTEMPTS = 3
API_RETRY_WAIT_SEC = 5
PIXABAY_BASE_URL = "https://pixabay.com/api/videos/"  # Fixes Pixabay base URL missing error

# Visual Branding Fallback
FONT_NAME = "Impact.ttf"

# STRICT YOUTUBE OAUTH SCOPES
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Stock Video API Keys Setup (GitHub Secrets friendly)
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "YOUR_PEXELS_KEY_HERE")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "YOUR_PIXABAY_KEY_HERE")
