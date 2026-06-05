import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "output" / "scripts"
AUDIO_DIR = BASE_DIR / "output" / "audio"
FINAL_VIDEOS_DIR = BASE_DIR / "output" / "final_videos"
FONTS_DIR = BASE_DIR / "fonts"
MEDIA_DIR = BASE_DIR / "output" / "media"
VIDEO_DIR = BASE_DIR / "output" / "media"

for d in [SCRIPTS_DIR, AUDIO_DIR, FINAL_VIDEOS_DIR, FONTS_DIR, MEDIA_DIR, VIDEO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

MEDIA_PER_KEYWORD = 3
MEDIA_ORIENTATION = "portrait"
MEDIA_MIN_DURATION = 3
MEDIA_MAX_DURATION = 15

SUBTITLE_ANIMATION_STYLE = "pop"
CAPTION_COLOR = "yellow"
HIGHLIGHT_COLOR = "green"

PEXELS_BASE_URL = "https://api.pexels.com/videos/"
PIXABAY_BASE_URL = "https://pixabay.com/api/videos/"

API_RETRY_ATTEMPTS = 3
API_RETRY_WAIT_SEC = 5
API_TIMEOUT_SEC = 30

FONT_NAME = "AmericanCaptain-MdEY.otf"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
