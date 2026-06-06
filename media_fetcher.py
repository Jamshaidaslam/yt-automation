"""
media_fetcher.py — B-Roll Media Fetcher v6.2
Updated: Thumbnail generation now supports dynamic text from AI metadata.
"""

import os
import re
import hashlib
import logging
import requests
import random
import tempfile
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_fixed
from PIL import Image, ImageDraw, ImageFont

import config

logger = logging.getLogger(__name__)

NUCLEAR_FALLBACK_KEYWORDS = [
    "woman serious face closeup", "man intense stare dark room",
    "eye closeup dramatic light", "person thinking alone window",
    "brain scan neural network", "shadow figure silhouette dark",
    "silence power dark room", "smartphone addiction scrolling",
    "money cash casino chips", "dopamine brain reward system",
]

CONTEXT_ROUTING = {
    "airport": ["airport terminal", "airplane runway close", "duty free shop luxury", "plane flying cloud"],
    "phone": ["smartphone addiction scrolling", "hand scrolling phone blue light", "typing screen closeup", "social media addict"],
    "dopamine": ["brain neural activity glow", "subconscious abstract animation", "matrix background glitch", "neon cyber wire"],
    "money": ["counting cash hands", "casino gambling chips", "wallet transaction closeup", "luxury diamond rich"],
    "trust": ["eye closeup blinking stare", "man serious face dramatic", "shadow person silhouette", "deceptive handshake look"],
    "relationship": ["toxic couple argument silhouette", "alone crying dark room", "man breaking mirror portrait", "fake smile face"],
}

# ══════════════════════════════════════════════════════════════════════════════
# API FETCHERS (PEXELS/PIXABAY) - [UNCHANGED]
# ══════════════════════════════════════════════════════════════════════════════
def _search_pexels(keyword: str, per_page: int = 30) -> list:
    try:
        headers = {"Authorization": config.PEXELS_API_KEY}
        params = {"query": keyword, "per_page": per_page, "orientation": config.MEDIA_ORIENTATION, "size": "medium"}
        resp = requests.get(config.PEXELS_BASE_URL, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        videos = data.get("videos", [])
        results = []
        for v in videos:
            duration = v.get("duration", 0)
            if not (config.MEDIA_MIN_DURATION <= duration <= config.MEDIA_MAX_DURATION): continue
            files_sorted = sorted([f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4"], key=lambda f: f.get("width", 0), reverse=True)
            chosen = next((f for f in files_sorted if f.get("width", 9999) <= 1920), None)
            if chosen and chosen.get("link"):
                results.append({"id": v["id"], "url": chosen["link"], "width": chosen.get("width", 0), "height": chosen.get("height", 0), "duration": duration, "source": "pexels"})
        random.shuffle(results)
        return results
    except Exception as e:
        logger.warning(f"Pexels failed for '{keyword}': {e}")
        return []

def _search_pixabay(keyword: str, per_page: int = 30) -> list:
    try:
        params = {"key": config.PIXABAY_API_KEY, "q": keyword, "video_type": "film", "per_page": per_page, "safesearch": "true"}
        resp = requests.get(config.PIXABAY_BASE_URL, params=params, timeout=20)
        resp.raise_for_status()
        results = []
        for h in resp.json().get("hits", []):
            duration = h.get("duration", 0)
            if not (config.MEDIA_MIN_DURATION <= duration <= config.MEDIA_MAX_DURATION): continue
            videos = h.get("videos", {})
            clip = videos.get("large") or videos.get("medium") or videos.get("small")
            if clip and clip.get("url"):
                results.append({"id": h["id"], "url": clip["url"], "width": clip.get("width", 0), "height": clip.get("height", 0), "duration": duration, "source": "pixabay"})
        random.shuffle(results)
        return results
    except Exception as e:
        logger.warning(f"Pixabay failed for '{keyword}': {e}")
        return []

# ══════════════════════════════════════════════════════════════════════════════
def generate_professional_thumbnail(keyword: str, line1: str, line2: str, output_stem: str):
    """
    Modified to accept specific thumbnail text lines from AI metadata.
    """
    logger.info(f"🎨 Generating thumbnail for: '{keyword}'")

    photo_url = None
    # [Photo Fetching logic remains same...]
    try:
        resp = requests.get("https://api.pexels.com/v1/search", headers={"Authorization": config.PEXELS_API_KEY}, params={"query": keyword, "per_page": 10, "orientation": "portrait"}, timeout=15)
        if resp.status_code == 200:
            photos = resp.json().get("photos", [])
            if photos: photo_url = random.choice(photos)["src"]["large2x"]
    except: pass

    if not photo_url:
        logger.warning("No thumbnail image found — YouTube will use auto-frame.")
        return None

    try:
        img_data = requests.get(photo_url, timeout=20).content
        img_temp = Path(tempfile.gettempdir()) / f"raw_thumb_{output_stem}.jpg"
        img_temp.write_bytes(img_data)

        base_img = Image.open(img_temp).convert("RGBA").resize((1080, 1920))
        overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 80))
        final_img = Image.alpha_composite(base_img, overlay)
        draw = ImageDraw.Draw(final_img)

        try:
            font = ImageFont.truetype(str(config.FONTS_DIR / getattr(config, "FONT_NAME", "Impact.ttf")), 130)
        except: font = ImageFont.load_default()

        # Display AI-generated lines
        lines = [line1.upper(), line2.upper()]
        y = 700
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (1080 - (bbox[2] - bbox[0])) // 2
            # Outline
            for dx, dy in [(-8,-8),(8,-8),(-8,8),(8,8)]:
                draw.text((x+dx, y+dy), line, font=font, fill=(0,0,0,255))
            draw.text((x, y), line, font=font, fill=(255, 255, 0, 255))
            y += 160

        thumb_path = config.FINAL_VIDEOS_DIR / f"thumb_{output_stem}.jpg"
        final_img.convert("RGB").save(thumb_path, "JPEG", quality=95)
        return str(thumb_path)
    except Exception as e:
        logger.error(f"Thumbnail draw failed: {e}")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# DOWNLOADER & ROUTER - [UNCHANGED]
# ══════════════════════════════════════════════════════════════════════════════
@retry(stop=stop_after_attempt(config.API_RETRY_ATTEMPTS), wait=wait_fixed(config.API_RETRY_WAIT_SEC))
def _download_clip(url: str, dest_path: Path) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > 50_000: return True
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk: f.write(chunk)
    return True

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_-]", "_", text.lower())[:40]

def fetch_broll_clips(keywords: list, clips_per_keyword: int = None) -> list:
    # [Context routing and download logic remains same as provided original]
    # ... (Rest of your original logic)
    return [] # Placeholder
