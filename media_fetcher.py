"""
media_fetcher.py — B-Roll Media Fetcher v6.3 (STABLE PRODUCTION BUILD)
Fixes:
- Completed fetch_broll_clips logic
- Fixed Pexels video endpoint
- Added smart routing + scoring
- Improved fallback system
- Added safety checks
"""

import os
import re
import random
import logging
import requests
import tempfile
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_fixed
from PIL import Image, ImageDraw, ImageFont

import config

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════
# FALLBACK SYSTEMS
# ═══════════════════════════════════════

NUCLEAR_FALLBACK_KEYWORDS = [
    "woman serious face closeup", "man intense stare dark room",
    "eye closeup dramatic light", "person thinking alone window",
    "brain scan neural network", "shadow figure silhouette dark",
    "silence power dark room", "smartphone addiction scrolling",
    "money cash casino chips", "dopamine brain reward system",
]

CONTEXT_ROUTING = {
    "airport": ["airport terminal", "airplane runway close", "duty free shop luxury", "plane flying cloud"],
    "phone": ["smartphone addiction scrolling", "hand scrolling phone blue light", "typing screen closeup"],
    "dopamine": ["brain neural activity glow", "neural network animation", "matrix glitch background"],
    "money": ["counting cash hands", "casino gambling chips", "luxury wealth lifestyle"],
    "trust": ["eye closeup blinking stare", "serious man face dramatic light", "shadow silhouette"],
    "relationship": ["couple argument silhouette", "alone crying dark room", "broken heart metaphor"],
}

# ═══════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════

def _ensure_dirs():
    try:
        config.FINAL_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    except:
        pass


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_-]", "_", text.lower())[:40]


def _score_keyword(keyword: str, topic: str) -> int:
    score = 0
    if topic.lower() in keyword.lower():
        score += 5
    for k in CONTEXT_ROUTING:
        if k in topic.lower() and keyword in CONTEXT_ROUTING[k]:
            score += 10
    return score


# ═══════════════════════════════════════
# PEXELS VIDEO FETCH (FIXED)
# ═══════════════════════════════════════

def _search_pexels(keyword: str, per_page: int = 30) -> list:
    try:
        headers = {"Authorization": config.PEXELS_API_KEY}

        # FIXED ENDPOINT
        url = "https://api.pexels.com/videos/search"

        params = {
            "query": keyword,
            "per_page": per_page,
            "orientation": getattr(config, "MEDIA_ORIENTATION", "portrait")
        }

        resp = requests.get(url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()

        data = resp.json()
        videos = data.get("videos", [])

        results = []

        for v in videos:
            duration = v.get("duration", 0)

            if not (config.MEDIA_MIN_DURATION <= duration <= config.MEDIA_MAX_DURATION):
                continue

            files = v.get("video_files", [])
            files_sorted = sorted(files, key=lambda f: f.get("width", 0), reverse=True)

            chosen = next(
                (f for f in files_sorted if f.get("width", 9999) <= 1920),
                None
            )

            if chosen and chosen.get("link"):
                results.append({
                    "id": v["id"],
                    "url": chosen["link"],
                    "width": chosen.get("width", 0),
                    "height": chosen.get("height", 0),
                    "duration": duration,
                    "source": "pexels"
                })

        return results

    except Exception as e:
        logger.warning(f"Pexels failed for '{keyword}': {e}")
        return []


# ═══════════════════════════════════════
# PIXABAY FETCH
# ═══════════════════════════════════════

def _search_pixabay(keyword: str, per_page: int = 30) -> list:
    try:
        params = {
            "key": config.PIXABAY_API_KEY,
            "q": keyword,
            "video_type": "film",
            "per_page": per_page,
            "safesearch": "true"
        }

        resp = requests.get(config.PIXABAY_BASE_URL, params=params, timeout=20)
        resp.raise_for_status()

        results = []

        for h in resp.json().get("hits", []):
            duration = h.get("duration", 0)

            if not (config.MEDIA_MIN_DURATION <= duration <= config.MEDIA_MAX_DURATION):
                continue

            videos = h.get("videos", {})
            clip = videos.get("large") or videos.get("medium") or videos.get("small")

            if clip and clip.get("url"):
                results.append({
                    "id": h["id"],
                    "url": clip["url"],
                    "width": clip.get("width", 0),
                    "height": clip.get("height", 0),
                    "duration": duration,
                    "source": "pixabay"
                })

        return results

    except Exception as e:
        logger.warning(f"Pixabay failed for '{keyword}': {e}")
        return []


# ═══════════════════════════════════════
# THUMBNAIL GENERATOR (FIXED + SAFE)
# ═══════════════════════════════════════

def generate_professional_thumbnail(keyword: str, line1: str, line2: str, output_stem: str):

    logger.info(f"🎨 Thumbnail: {keyword}")

    _ensure_dirs()

    photo_url = None

    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": config.PEXELS_API_KEY},
            params={"query": keyword, "per_page": 10, "orientation": "portrait"},
            timeout=15
        )

        if resp.status_code == 200:
            photos = resp.json().get("photos", [])
            if photos:
                photo_url = random.choice(photos)["src"]["large2x"]

    except Exception as e:
        logger.warning(f"Thumbnail fetch failed: {e}")

    if not photo_url:
        return None

    try:
        img_data = requests.get(photo_url, timeout=20).content

        temp_path = Path(tempfile.gettempdir()) / f"thumb_{output_stem}.jpg"
        temp_path.write_bytes(img_data)

        base = Image.open(temp_path).convert("RGBA").resize((1080, 1920))

        overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 90))
        img = Image.alpha_composite(base, overlay)

        draw = ImageDraw.Draw(img)

        try:
            font_path = config.FONTS_DIR / getattr(config, "FONT_NAME", "Impact.ttf")
            font = ImageFont.truetype(str(font_path), 110)
        except:
            font = ImageFont.load_default()

        lines = [line1.upper(), line2.upper()]
        y = 650

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (1080 - (bbox[2] - bbox[0])) // 2

            # outline
            for dx, dy in [(-5,-5),(5,-5),(-5,5),(5,5)]:
                draw.text((x+dx, y+dy), line, font=font, fill=(0,0,0,255))

            draw.text((x, y), line, font=font, fill=(255, 230, 0, 255))
            y += 170

        out_path = config.FINAL_VIDEOS_DIR / f"thumb_{output_stem}.jpg"
        img.convert("RGB").save(out_path, "JPEG", quality=95)

        return str(out_path)

    except Exception as e:
        logger.error(f"Thumbnail error: {e}")
        return None


# ═══════════════════════════════════════
# DOWNLOAD ENGINE
# ═══════════════════════════════════════

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def _download_clip(url: str, dest_path: Path) -> bool:

    if dest_path.exists() and dest_path.stat().st_size > 50_000:
        return True

    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()

        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    return True


# ═══════════════════════════════════════
# MAIN ENGINE (FIXED COMPLETE)
# ═══════════════════════════════════════

def fetch_broll_clips(keywords: list, clips_per_keyword: int = 2) -> list:

    _ensure_dirs()

    all_results = []

    for topic in keywords:

        topic_results = []

        routing_hits = []

        for k, v in CONTEXT_ROUTING.items():
            if k in topic.lower():
                routing_hits.extend(v)

        search_pool = routing_hits if routing_hits else NUCLEAR_FALLBACK_KEYWORDS

        search_pool = sorted(
            search_pool,
            key=lambda x: _score_keyword(x, topic),
            reverse=True
        )

        search_pool = search_pool[:clips_per_keyword + 2]

        for kw in search_pool:

            pexels = _search_pexels(kw)
            pixabay = _search_pixabay(kw)

            combined = pexels + pixabay

            for c in combined:
                c["topic"] = topic
                c["keyword"] = kw

            topic_results.extend(combined)

            if len(topic_results) >= clips_per_keyword:
                break

        if not topic_results:
            fallback_kw = random.choice(NUCLEAR_FALLBACK_KEYWORDS)
            topic_results = _search_pexels(fallback_kw) + _search_pixabay(fallback_kw)

        all_results.extend(topic_results[:clips_per_keyword])

    return all_results
