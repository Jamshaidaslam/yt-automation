"""
media_fetcher.py — B-Roll Media & Clickable Thumbnail Downloader
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import os
import re
import hashlib
import logging
import requests
import random    # 🌟 Added for randomness and diversity
import tempfile  # 🌟 FIXED: Added missing import to prevent NameError during thumbnail compilation
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_fixed
from PIL import Image, ImageDraw, ImageFont  # 🌟 Added for professional thumbnail rendering

import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# ═══════════════════════════════════════════════════════════════════════════════
# PEXELS VIDEO SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

def _search_pexels(keyword: str, per_page: int = 30) -> list[dict]:
    """Call Pexels Videos search API."""
    headers = {"Authorization": config.PEXELS_API_KEY}
    params  = {
        "query":       keyword,
        "per_page":    per_page,
        "orientation": config.MEDIA_ORIENTATION,  # "portrait"
        "size":        "medium",
    }

    resp = requests.get(config.PEXELS_BASE_URL, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    videos = data.get("videos", [])
    results = []

    for v in videos:
        duration = v.get("duration", 0)
        if not (config.MEDIA_MIN_DURATION <= duration <= config.MEDIA_MAX_DURATION):
            continue

        files = v.get("video_files", [])
        files_sorted = sorted(
            [f for f in files if f.get("file_type") == "video/mp4"],
            key=lambda f: f.get("width", 0),
            reverse=True,
        )

        chosen = None
        for f in files_sorted:
            if f.get("width", 9999) <= 1920:
                chosen = f
                break
        if chosen is None and files_sorted:
            chosen = files_sorted[-1]

        if chosen and chosen.get("link"):
            results.append({
                "id":       v["id"],
                "url":      chosen["link"],
                "width":    chosen.get("width", 0),
                "height":   chosen.get("height", 0),
                "duration": duration,
                "source":   "pexels",
            })

    random.shuffle(results)
    logger.info(f"Pexels '{keyword}': {len(results)} usable clips found & shuffled.")
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# PIXABAY VIDEO SEARCH (Fallback)
# ═══════════════════════════════════════════════════════════════════════════════

def _search_pixabay(keyword: str, per_page: int = 30) -> list[dict]:
    """Call Pixabay Videos API."""
    params = {
        "key":          config.PIXABAY_API_KEY,
        "q":            keyword,
        "video_type":   "film",
        "per_page":     per_page,
        "safesearch":   "true",
    }

    resp = requests.get(config.PIXABAY_BASE_URL, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    hits    = data.get("hits", [])
    results = []

    for h in hits:
        videos = h.get("videos", {})
        clip = (
            videos.get("large")
            or videos.get("medium")
            or videos.get("small")
        )
        if not clip:
            continue

        duration = h.get("duration", 0)
        if not (config.MEDIA_MIN_DURATION <= duration <= config.MEDIA_MAX_DURATION):
            continue

        url = clip.get("url", "")
        if not url:
            continue

        results.append({
            "id":       h["id"],
            "url":      url,
            "width":    clip.get("width", 0),
            "height":   clip.get("height", 0),
            "duration": duration,
            "source":   "pixabay",
        })

    random.shuffle(results)
    logger.info(f"Pixabay '{keyword}': {len(results)} usable clips found & shuffled.")
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# 🌟 PROFESSIONAL AUTOMATIC THUMBNAIL GENERATOR 🌟
# ═══════════════════════════════════════════════════════════════════════════════

def generate_professional_thumbnail(keyword: str, hook_text: str, output_stem: str) -> str | None:
    """
    Fetches a high-resolution portrait image based on the keyword and bakes 
    an aggressive, eye-catching, clickable text overlay onto it.
    """
    logger.info(f"🎨 Generating high-retention thumbnail for topic: '{keyword}'")
    
    # 1. Fetch Image from Pexels Photo API
    photo_url = None
    headers = {"Authorization": config.PEXELS_API_KEY}
    params = {"query": keyword, "per_page": 10, "orientation": "portrait"}
    
    try:
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            photos = resp.json().get("photos", [])
            if photos:
                photo_url = random.choice(photos)["src"]["large2x"]
    except Exception as e:
        logger.warning(f"Failed to fetch image from Pexels, trying Pixabay: {e}")

    # Fallback to Pixabay Image API if Pexels fails
    if not photo_url:
        try:
            pixabay_img_url = f"https://pixabay.com/api/?key={config.PIXABAY_API_KEY}&q={requests.utils.quote(keyword)}&image_type=photo&orientation=vertical"
            resp = requests.get(pixabay_img_url, timeout=15)
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                if hits:
                    photo_url = random.choice(hits)["largeImageURL"]
        except Exception as e:
            logger.error(f"Image API fallback failed: {e}")

    if not photo_url:
        logger.warning("❌ Could not fetch unique thumbnail image. System will default to YouTube auto-frame.")
        return None

    # 2. Download Image and Process Graphic Overlay
    try:
        img_data = requests.get(photo_url, timeout=20).content
        img_temp = Path(tempfile.gettempdir()) / f"raw_thumb_{output_stem}.jpg"
        with open(img_temp, "wb") as f:
            f.write(img_data)

        # Base Configs for 9:16 Shorts Thumbnail
        t_w, t_h = 1080, 1920
        base_img = Image.open(img_temp).convert("RGBA").resize((t_w, t_h))
        
        # Dark dramatic vignetting layer to pop the text
        overlay = Image.new("RGBA", (t_w, t_h), (0, 0, 0, 80)) # Subtle dark tint
        final_img = Image.alpha_composite(base_img, overlay)
        draw = ImageDraw.Draw(final_img)

        # Load bold font
        try:
            font_name = getattr(config, "FONT_NAME", "Impact.ttf")
            font_path = config.FONTS_DIR / font_name
            font = ImageFont.truetype(str(font_path), 110) # Massive clickable text
        except Exception:
            font = ImageFont.load_default()

        # Wrap text elegantly so it doesn't leave the screen margins
        wrapped_lines = []
        for phrase in hook_text.split("\n"):
            wrapped_lines.extend(re.sub(r'\s+', ' ', phrase).strip().split(" "))
        
        # Group into 2-3 impact words per line
        lines = []
        for i in range(0, len(wrapped_lines), 2):
            lines.append(" ".join(wrapped_lines[i:i+2]).upper())

        # Draw heavy stroke outlines + custom bright text colors
        current_y = int(t_h * 0.35)
        for line in lines[:4]:  # Keep it ultra clean, max 4 lines
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            x = (t_w - w) // 2

            # Dynamic toxic color scheming (Yellow/Green)
            text_color = (255, 255, 0, 255) if len(line) % 2 == 0 else (57, 255, 20, 255)
            
            # Heavy Black Outline for maximum legibility over raw scenes
            for adj_x, adj_y in [(-8, -8), (8, -8), (-8, 8), (8, 8), (-6, 0), (6, 0), (0, -6), (0, 6)]:
                draw.text((x + adj_x, current_y + adj_y), line, font=font, fill=(0, 0, 0, 255))
            
            draw.text((x, current_y), line, font=font, fill=text_color)
            current_y += 140

        # Save out clean thumbnail image
        thumb_path = config.FINAL_VIDEOS_DIR / f"thumb_{output_stem}.jpg"
        final_img.convert("RGB").save(thumb_path, "JPEG", quality=95)
        
        if img_temp.exists():
            os.remove(img_temp)
            
        logger.info(f"✅ Clickable Professional Thumbnail Generated successfully: {thumb_path.name}")
        return str(thumb_path)

    except Exception as e:
        logger.error(f"Error drawing thumbnail layout: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# DOWNLOADER CORE
# ═══════════════════════════════════════════════════════════════════════════════

@retry(stop=stop_after_attempt(config.API_RETRY_ATTEMPTS),
       wait=wait_fixed(config.API_RETRY_WAIT_SEC))
def _
