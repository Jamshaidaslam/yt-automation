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

# Video Specs
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
MEDIA_PER_KEYWORD = 3

# API Retry Configuration (Fixes media_fetcher.py error)
API_RETRY_ATTEMPTS = 3

# Visual Branding Fallback
FONT_NAME = "Impact.ttf"

# STRICT YOUTUBE OAUTH SCOPES (Fixed line-break bug)
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
