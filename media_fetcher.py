"""
media_fetcher.py — B-Roll Media Fetcher v6.2
Fallback: Pexels → Pixabay → Nuclear Keywords → Local Assets
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
    "woman serious face closeup",
    "man intense stare dark room",
    "eye closeup dramatic light",
    "person thinking alone window",
    "brain scan neural network",
    "shadow figure silhouette dark",
    "silence power dark room",
    "smartphone addiction scrolling",
    "money cash casino chips",
    "dopamine brain reward system",
]

CONTEXT_ROUTING = {
    "airport":      ["airport terminal", "airplane runway close", "duty free shop luxury", "plane flying cloud"],
    "phone":        ["smartphone addiction scrolling", "hand scrolling phone blue light", "typing screen closeup", "social media addict"],
    "dopamine":     ["brain neural activity glow", "subconscious abstract animation", "matrix background glitch", "neon cyber wire"],
    "money":        ["counting cash hands", "casino gambling chips", "wallet transaction closeup", "luxury diamond rich"],
    "trust":        ["eye closeup blinking stare", "man serious face dramatic", "shadow person silhouette", "deceptive handshake look"],
    "relationship": ["toxic couple argument silhouette", "alone crying dark room", "man breaking mirror portrait", "fake smile face"],
}


# ══════════════════════════════════════════════════════════════════════════════
def _search_pexels(keyword: str, per_page: int = 30) -> list:
    try:
        headers = {"Authorization": config.PEXELS_API_KEY}
        params  = {
            "query":       keyword,
            "per_page":    per_page,
            "orientation": config.MEDIA_ORIENTATION,
            "size":        "medium",
        }
        resp = requests.get(config.PEXELS_BASE_URL, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        data   = resp.json()
        videos = data.get("videos", [])

        results = []
        for v in videos:
            duration = v.get("duration", 0)
            if not (config.MEDIA_MIN_DURATION <= duration <= config.MEDIA_MAX_DURATION):
                continue

            files_sorted = sorted(
                [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4"],
                key=lambda f: f.get("width", 0),
                reverse=True,
            )
            chosen = next((f for f in files_sorted if f.get("width", 9999) <= 1920), None)
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
        logger.info(f"Pexels '{keyword}': {len(results)} clips")
        return results

    except Exception as e:
        logger.warning(f"Pexels failed for '{keyword}': {e}")
        return []


def _search_pixabay(keyword: str, per_page: int = 30) -> list:
    try:
        params = {
            "key":        config.PIXABAY_API_KEY,
            "q":          keyword,
            "video_type": "film",
            "per_page":   per_page,
            "safesearch": "true",
        }
        resp = requests.get(config.PIXABAY_BASE_URL, params=params, timeout=20)
        resp.raise_for_status()

        results = []
        for h in resp.json().get("hits", []):
            duration = h.get("duration", 0)
            if not (config.MEDIA_MIN_DURATION <= duration <= config.MEDIA_MAX_DURATION):
                continue

            videos = h.get("videos", {})
            clip   = videos.get("large") or videos.get("medium") or videos.get("small")
            if not clip or not clip.get("url"):
                continue

            results.append({
                "id":       h["id"],
                "url":      clip["url"],
                "width":    clip.get("width", 0),
                "height":   clip.get("height", 0),
                "duration": duration,
                "source":   "pixabay",
            })

        random.shuffle(results)
        logger.info(f"Pixabay '{keyword}': {len(results)} clips")
        return results

    except Exception as e:
        logger.warning(f"Pixabay failed for '{keyword}': {e}")
        return []


# ══════════════════════════════════════════════════════════════════════════════
def generate_professional_thumbnail(keyword: str, hook_text: str, output_stem: str):
    """Fetch a stock photo and overlay bold text for a clickable thumbnail."""
    logger.info(f"🎨 Generating thumbnail for: '{keyword}'")

    photo_url = None

    # Try Pexels photos
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": config.PEXELS_API_KEY},
            params={"query": keyword, "per_page": 10, "orientation": "portrait"},
            timeout=15,
        )
        if resp.status_code == 200:
            photos = resp.json().get("photos", [])
            if photos:
                photo_url = random.choice(photos)["src"]["large2x"]
    except Exception as e:
        logger.warning(f"Pexels photo fetch failed: {e}")

    # Try Pixabay photos
    if not photo_url:
        try:
            resp = requests.get(
                "https://pixabay.com/api/",
                params={
                    "key":          config.PIXABAY_API_KEY,
                    "q":            keyword,
                    "image_type":   "photo",
                    "orientation":  "vertical",
                    "per_page":     10,
                },
                timeout=15,
            )
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                if hits:
                    photo_url = random.choice(hits)["largeImageURL"]
        except Exception as e:
            logger.warning(f"Pixabay photo fetch failed: {e}")

    if not photo_url:
        logger.warning("No thumbnail image found — YouTube will use auto-frame.")
        return None

    try:
        img_data = requests.get(photo_url, timeout=20).content
        img_temp = Path(tempfile.gettempdir()) / f"raw_thumb_{output_stem}.jpg"
        img_temp.write_bytes(img_data)

        t_w, t_h = 1080, 1920
        base_img = Image.open(img_temp).convert("RGBA").resize((t_w, t_h))

        # Dark overlay for text readability
        overlay = Image.new("RGBA", (t_w, t_h), (0, 0, 0, 80))
        final_img = Image.alpha_composite(base_img, overlay)
        draw = ImageDraw.Draw(final_img)

        # Font loading
        try:
            font_name = getattr(config, "FONT_NAME", "Impact.ttf")
            font = ImageFont.truetype(str(config.FONTS_DIR / font_name), 110)
        except Exception:
            font = ImageFont.load_default()

        # Word wrap — 2 words per line
        words = re.sub(r"\s+", " ", hook_text.replace("\n", " ")).strip().split()
        lines = [" ".join(words[i:i+2]).upper() for i in range(0, len(words), 2)]

        y = int(t_h * 0.35)
        for line in lines[:4]:
            bbox = draw.textbbox((0, 0), line, font=font)
            x    = (t_w - (bbox[2] - bbox[0])) // 2
            color = (255, 255, 0, 255) if len(line) % 2 == 0 else (57, 255, 20, 255)
            # Outline
            for dx, dy in [(-8,-8),(8,-8),(-8,8),(8,8),(-6,0),(6,0),(0,-6),(0,6)]:
                draw.text((x+dx, y+dy), line, font=font, fill=(0,0,0,255))
            draw.text((x, y), line, font=font, fill=color)
            y += 140

        thumb_path = config.FINAL_VIDEOS_DIR / f"thumb_{output_stem}.jpg"
        final_img.convert("RGB").save(thumb_path, "JPEG", quality=95)

        try:
            img_temp.unlink()
        except Exception:
            pass

        logger.info(f"✅ Thumbnail saved: {thumb_path.name}")
        return str(thumb_path)

    except Exception as e:
        logger.error(f"Thumbnail draw failed: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
@retry(
    stop=stop_after_attempt(config.API_RETRY_ATTEMPTS),
    wait=wait_fixed(config.API_RETRY_WAIT_SEC),
)
def _download_clip(url: str, dest_path: Path) -> bool:
    # BUG FIX 1: stat() on non-existent file raises FileNotFoundError — check exists() first
    if dest_path.exists() and dest_path.stat().st_size > 50_000:
        logger.info(f"Cache hit: {dest_path.name}")
        return True

    logger.info(f"Downloading: {url[:80]}…")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk:                    # BUG FIX 2: skip empty keep-alive chunks
                    f.write(chunk)

    # BUG FIX 3: verify file wrote correctly before returning True
    if not dest_path.exists() or dest_path.stat().st_size < 50_000:
        dest_path.unlink(missing_ok=True)
        raise RuntimeError(f"Downloaded file too small or missing: {dest_path.name}")

    logger.info(f"Saved → {dest_path.name} ({dest_path.stat().st_size // 1024} KB)")
    return True


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_-]", "_", text.lower())[:40]


# ══════════════════════════════════════════════════════════════════════════════
def fetch_broll_clips(keywords: list, clips_per_keyword: int = None) -> list:
    """
    Fetch and download B-roll clips.
    Fallback chain: Pexels → Pixabay → Nuclear keywords → Local cache.
    """
    if clips_per_keyword is None:
        clips_per_keyword = getattr(config, "MEDIA_PER_KEYWORD", 2)

    downloads_dir = Path(getattr(config, "DOWNLOADS_DIR", "downloads"))
    downloads_dir.mkdir(parents=True, exist_ok=True)

    # Diagnose API keys early — most common cause of zero clips
    pexels_key   = getattr(config, "PEXELS_API_KEY",   None)
    pixabay_key  = getattr(config, "PIXABAY_API_KEY",  None)
    if not pexels_key or pexels_key == "YOUR_KEY_HERE":
        logger.warning("⚠️  PEXELS_API_KEY is not set — Pexels search will fail.")
    if not pixabay_key or pixabay_key == "YOUR_KEY_HERE":
        logger.warning("⚠️  PIXABAY_API_KEY is not set — Pixabay search will fail.")

    logger.info(f"📁 Downloads dir: {downloads_dir.resolve()}")
    logger.info(f"🎯 clips_per_keyword={clips_per_keyword}, keywords={keywords}")

    all_paths: list  = []
    seen_ids:  set   = set()

    # ── Context routing ───────────────────────────────────────────────────────
    raw_keywords   = [k.strip() for k in keywords if k.strip()]
    joined_queries = " ".join(raw_keywords).lower()

    active_keywords = []
    for trigger, brolls in CONTEXT_ROUTING.items():
        if trigger in joined_queries:
            logger.info(f"Context lock → [{trigger.upper()}]")
            active_keywords = brolls
            break

    if not active_keywords:
        active_keywords = raw_keywords or random.sample(NUCLEAR_FALLBACK_KEYWORDS, 3)

    # ── Phase 1 & 2: Pexels → Pixabay per keyword ────────────────────────────
    for keyword in active_keywords:
        candidates = _search_pexels(keyword, per_page=20)
        if not candidates:
            candidates = _search_pixabay(keyword, per_page=20)

        downloaded = 0
        for clip in candidates:
            if downloaded >= clips_per_keyword:
                break

            clip_id = f"{clip['source']}_{clip['id']}"
            if clip_id in seen_ids:
                continue

            uid       = hashlib.md5(clip["url"].encode()).hexdigest()[:10]
            dest_path = downloads_dir / f"broll_{_slug(keyword)}_{uid}.mp4"

            try:
                if _download_clip(clip["url"], dest_path):
                    all_paths.append(str(dest_path))
                    seen_ids.add(clip_id)
                    downloaded += 1
            except Exception as e:
                logger.warning(f"Download failed ({clip['url'][:60]}): {e}")

    # ── Phase 3: Nuclear fallback keywords ───────────────────────────────────
    if not all_paths:
        logger.warning("No clips from main keywords — trying nuclear fallbacks...")
        for fb_kw in random.sample(NUCLEAR_FALLBACK_KEYWORDS, 4):
            candidates = _search_pexels(fb_kw, per_page=15) or _search_pixabay(fb_kw, per_page=15)
            for clip in candidates[:clips_per_keyword]:
                uid       = hashlib.md5(clip["url"].encode()).hexdigest()[:10]
                dest_path = downloads_dir / f"fallback_{_slug(fb_kw)}_{uid}.mp4"
                try:
                    if _download_clip(clip["url"], dest_path):
                        all_paths.append(str(dest_path))
                except Exception:
                    continue
            if len(all_paths) >= 4:
                break

    # ── Phase 4: Local cache ──────────────────────────────────────────────────
    if not all_paths:
        logger.warning("APIs returned nothing — searching local cache...")
        local_assets = [
            str(p) for p in downloads_dir.glob("*.mp4")
            if p.stat().st_size > 50_000
        ]
        if not local_assets:
            emergency = Path("assets/videos")
            if emergency.exists():
                local_assets = [str(p) for p in emergency.glob("*.mp4")]

        if local_assets:
            all_paths = random.sample(local_assets, min(len(local_assets), 5))
            logger.info(f"Recovered {len(all_paths)} clips from local cache.")
        else:
            raise RuntimeError("No clips available via API or local cache.")

    logger.info(f"✅ Total clips ready: {len(all_paths)}")
    return all_paths
