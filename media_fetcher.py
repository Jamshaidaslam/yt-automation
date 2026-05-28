"""
media_fetcher.py — B-Roll Media Downloader
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
Strategy:
  1. Query Pexels Videos API for each keyword.
  2. If Pexels returns 0 usable results → automatically fall back to Pixabay.
  3. Download each clip to ./output/media/<slug>.mp4
  4. Return ordered list of local file paths for the video compiler.

All downloads are skipped if the target file already exists (caching for re-runs).
"""

import os
import re
import hashlib
import logging
import requests
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_fixed

import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# ═══════════════════════════════════════════════════════════════════════════════
# PEXELS
# ═══════════════════════════════════════════════════════════════════════════════

def _search_pexels(keyword: str, per_page: int = 15) -> list[dict]:
    """
    Call Pexels Videos search API.
    Returns list of video metadata dicts with keys: id, url, width, height, duration.
    """
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
            continue  # Skip clips that are too short or too long

        # Prefer HD (1280+ width) but accept anything portrait
        files = v.get("video_files", [])
        # Sort by width descending, prefer portrait files
        files_sorted = sorted(
            [f for f in files if f.get("file_type") == "video/mp4"],
            key=lambda f: f.get("width", 0),
            reverse=True,
        )

        # Take the first file ≤ 1920px wide to avoid unnecessarily large downloads
        chosen = None
        for f in files_sorted:
            if f.get("width", 9999) <= 1920:
                chosen = f
                break
        if chosen is None and files_sorted:
            chosen = files_sorted[-1]  # Fallback to smallest

        if chosen and chosen.get("link"):
            results.append({
                "id":       v["id"],
                "url":      chosen["link"],
                "width":    chosen.get("width", 0),
                "height":   chosen.get("height", 0),
                "duration": duration,
                "source":   "pexels",
            })

    logger.info(f"Pexels '{keyword}': {len(results)} usable clips found.")
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# PIXABAY  (fallback)
# ═══════════════════════════════════════════════════════════════════════════════

def _search_pixabay(keyword: str, per_page: int = 15) -> list[dict]:
    """
    Call Pixabay Videos API.
    Returns list of video metadata dicts (same schema as _search_pexels).
    """
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
        # Preference order: large → medium → small
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

    logger.info(f"Pixabay '{keyword}': {len(results)} usable clips found.")
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# DOWNLOADER
# ═══════════════════════════════════════════════════════════════════════════════

@retry(stop=stop_after_attempt(config.API_RETRY_ATTEMPTS),
       wait=wait_fixed(config.API_RETRY_WAIT_SEC))
def _download_clip(url: str, dest_path: Path) -> bool:
    """
    Stream-download a single video clip to dest_path.
    Returns True on success, raises on failure.
    """
    if dest_path.exists() and dest_path.stat().st_size > 50_000:
        logger.info(f"Cache hit: {dest_path.name}")
        return True

    logger.info(f"Downloading {url[:80]}…")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):  # 1 MB chunks
                f.write(chunk)
    logger.info(f"Saved → {dest_path.name} ({dest_path.stat().st_size // 1024} KB)")
    return True


def _slug(text: str) -> str:
    """Convert arbitrary text to a safe filename slug."""
    return re.sub(r"[^a-z0-9_-]", "_", text.lower())[:40]


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_broll_clips(keywords: list[str], clips_per_keyword: int = None) -> list[str]:
    """
    For each keyword: try Pexels → fallback to Pixabay if 0 results.
    Downloads up to `clips_per_keyword` clips per keyword.
    Returns a de-duplicated list of local file paths (str) ready for the compiler.

    Parameters
    ----------
    keywords : list[str]
        Search keywords from the Groq script output.
    clips_per_keyword : int
        Override config.MEDIA_PER_KEYWORD.
    """
    if clips_per_keyword is None:
        clips_per_keyword = config.MEDIA_PER_KEYWORD

    all_paths: list[str] = []
    seen_ids: set[str]   = set()  # Dedup by source+id

    for keyword in keywords:
        # ── 1. Try Pexels ────────────────────────────────────────────────────
        try:
            candidates = _search_pexels(keyword)
        except Exception as exc:
            logger.warning(f"Pexels error for '{keyword}': {exc}")
            candidates = []

        # ── 2. Fallback to Pixabay ──────────────────────────────────────────
        if not candidates:
            logger.info(f"No Pexels results for '{keyword}' → trying Pixabay…")
            try:
                candidates = _search_pixabay(keyword)
            except Exception as exc:
                logger.warning(f"Pixabay error for '{keyword}': {exc}")
                candidates = []

        if not candidates:
            logger.warning(f"No media found for keyword: '{keyword}' — skipping.")
            continue

        downloaded = 0
        for clip in candidates:
            if downloaded >= clips_per_keyword:
                break

            dedup_key = f"{clip['source']}_{clip['id']}"
            if dedup_key in seen_ids:
                continue
            seen_ids.add(dedup_key)

            # Build a deterministic filename from keyword + clip id
            fname = f"{_slug(keyword)}_{clip['source']}_{clip['id']}.mp4"
            dest  = config.MEDIA_DIR / fname

            try:
                ok = _download_clip(clip["url"], dest)
                if ok:
                    all_paths.append(str(dest))
                    downloaded += 1
            except Exception as exc:
                logger.warning(f"Download failed for {clip['url']}: {exc}")

    logger.info(f"Total B-roll clips ready: {len(all_paths)}")
    return all_paths


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_keywords = ["surveillance camera city", "hacker dark room", "data center servers"]
    paths = fetch_broll_clips(test_keywords, clips_per_keyword=2)
    for p in paths:
        print(p)
