"""
main.py — Pipeline Orchestrator (ANTI-SPAM & INTENT ALIGNED v2.6 - SYSTEM REPAIR FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fixed: Targeted precise config path mapping for asset cache purges.
Fixed: Protected thumbnail rendering sequence with absolute safety catch blocks.
Tested: Bracket alignment and Python 3.10+ syntax error-free.
─────────────────────────────────────────────────────────────────────────────────────
"""

import argparse
import json
import logging
import sys
import time
import os
import shutil
import random
from datetime import datetime, timedelta
from pathlib import Path

try:
    import config
    HAS_CONFIG_FILE = True
except ImportError:
    HAS_CONFIG_FILE = False

SCRIPTS_DIR = Path(config.SCRIPTS_DIR) if HAS_CONFIG_FILE else Path("output/scripts")
MEDIA_PER_KEYWORD = config.MEDIA_PER_KEYWORD if HAS_CONFIG_FILE else 3

SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

import script_generator
import media_fetcher
import audio_generator
import video_compiler
import uploader

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

# Duplicate prevention — upload log file
UPLOAD_LOG = Path("output/upload_log.json")
UPLOAD_LOG.parent.mkdir(parents=True, exist_ok=True)


def generate_psychology_hook_title(raw_title: str) -> str:
    """
    🌟 NEW HUMAN INJECTION ENGINE
    Takes a raw or incomplete title/topic from Groq and converts it into a
    high-retention, properly cased, automated clickbait title with dynamic emojis.
    """
    # Clean up the input string (remove hashtags if any)
    clean_topic = raw_title.split("#")[0].strip().title()
    
    # Generic replacement block to keep the core theme intact
    if not clean_topic or clean_topic.lower() in ["dark reality", "psychology fact", "video"]:
        clean_topic = "Your Subconscious"

    # High CTR Psychological Trigger Patterns (screenshot style optimized)
    templates = [
        f"Your Brain Has A Backdoor: {clean_topic} 🧠",
        f"The Dark Secret Your Brain Hides From You About {clean_topic} 🤫",
        f"Your Mind Is Not Your Own: The {clean_topic} Glitch 👤",
        f"Why You're Sabotaging Yourself On Purpose With {clean_topic} 💀",
        f"Your Eyes Betray You Every Time On {clean_topic} 👀",
        f"Your Subconscious Is Controlling You via {clean_topic} 👁️",
        f"The Hidden World Of {clean_topic} Awareness 🌌",
        f"Silence Destroys Them Silently: {clean_topic} 🔕",
        f"How Your Phone Uses {clean_topic} As A Dopamine Trap 📱"
    ]
    
    # Random select patterns to avoid channel duplicate spam penalties
    selected_title = random.choice(templates)
    return selected_title[:95]  # Cap under 100 char limit for Shorts/Reels algorithm


def _load_upload_log() -> list:
    """Purane uploads ka record load karo."""
    if UPLOAD_LOG.exists():
        try:
            return json.loads(UPLOAD_LOG.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_upload_log(log: list):
    """Upload record save karo."""
    UPLOAD_LOG.write_text(json.dumps(log, indent=2), encoding="utf-8")


def _was_recently_uploaded(minutes: int = 45) -> bool:
    """Check karo ke kya last X minutes mein video upload ho chuki hai."""
    log = _load_upload_log()
    if not log:
        return False
    last_entry = log[-1]
    last_time = datetime.fromisoformat(last_entry.get("timestamp", "2000-01-01"))
    diff = datetime.now() - last_time
    if diff < timedelta(minutes=minutes):
        logger.warning(
            f"⚠️ Duplicate prevention active — last upload was {int(diff.total_seconds() / 60)} minutes ago. Skipping."
        )
        return True
    return False


def _log_upload(stem: str, results: dict):
    """Successful upload ko log mein save karo."""
    log = _load_upload_log()
    log.append({
        "timestamp": datetime.now().isoformat(),
        "stem": stem,
        "results": results
    })
    if len(log) > 100:
        log = log[-100:]
    _save_upload_log(log)


def _cleanup_old_cache_folders():
    """🔥 CRITICAL FIXED: Targets precise config mapping paths instead of ghost dirs to prevent repeat loops."""
    target_dirs = []
    if HAS_CONFIG_FILE and hasattr(config, "MEDIA_DIR"):
        target_dirs.append(Path(config.MEDIA_DIR))
    else:
        target_dirs.append(Path("output/media"))
        
    for folder in target_dirs:
        if folder.exists():
            logger.info(f"🧹 Clearing core video stock database assets cache: {folder}")
            for item in folder.iterdir():
                try:
                    if item.is_file() and not item.name.startswith("."):
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception as e:
                    logger.warning(f"Could not purge cash segment {item}: {e}")


def run_pipeline(topic: str | None = None, skip_upload: bool = False) -> dict:
    start_time = time.time()
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem       = f"video_{timestamp}"

    logger.info("=" * 60)
    logger.info(f"🚀 STARTING ANTI-SPAM PIPELINE SESSION: {stem.upper()}")
    logger.info("=" * 60)

    # DUPLICATE PREVENTION CHECK
    if not skip_upload and _was_recently_uploaded(minutes=45):
        logger.info("Pipeline halted — duplicate upload prevention triggered.")
        logger.info("=" * 60)
        sys.exit(0)

    # 🔥 Clears the exact active stock directory before download execution
    _cleanup_old_cache_folders()

    # STEP 1: Script Generation
    logger.info("STEP 1/5 — Invoking Groq LLM for script engineering…")
    script_data = script_generator.generate_script(topic=topic)
    
    # Extract raw title and inject automated high-CTR psychological hook
    seo_block = script_data.get("seo", {})
    raw_title = seo_block.get("title") or script_data.get("title") or topic or "Dark Psychology"
    
    # Generate the high-retention structured title
    human_optimized_title = generate_psychology_hook_title(raw_title)
    logger.info(f"🎯 Automated Clickbait Title Locked: '{human_optimized_title}'")
    
    # Back-inject inside the script memory so ALL subsequent components read the same title
    if "seo" not in script_data:
        script_data["seo"] = {}
    script_data["seo"]["title"] = human_optimized_title
    script_data["title"] = human_optimized_title

    script_output = SCRIPTS_DIR / f"{stem}.json"
    script_output.write_text(json.dumps(script_data, indent=2), encoding="utf-8")

    # STEP 2: Media Asset Procurement
    logger.info("STEP 2/5 — Querying stock video download engines…")

    keywords_list = (
        script_data.get("broll_keywords")
        or script_data.get("search_keywords")
        or script_data.get("keywords")
    )

    if not keywords_list or not isinstance(keywords_list, list) or len(keywords_list) == 0:
        logger.warning("Groq dynamic key failed. Injecting high-retention fallbacks.")
        keywords_list = [
            "dark aesthetic cinematic",
            "mysterious silhouette shadow",
            "brain neural activity glow",
            "closeup eye fear thriller"
        ]

    logger.info(f"Targeting visual database: {keywords_list}")
    media_paths = media_fetcher.fetch_broll_clips(
        keywords          = keywords_list,
        clips_per_keyword = MEDIA_PER_KEYWORD,
    )

    if not media_paths:
        logger.error("Pipeline failure: No B-roll fetched.")
        sys.exit(1)

    # 🌟 STEP 2.5: Professional Automatic Thumbnail Generation (Wrapped with absolute fallback guard) 🌟
    logger.info("STEP 2.5 — Generating Eye-Catching Clickable Thumbnail Image…")
    thumbnail_path = None
    try:
        thumb_keyword = keywords_list[0] if keywords_list else "dark mystery"
        hook_text = script_data["seo"]["title"].split(":")[0].strip() # Takes core hook phrase
        
        thumbnail_path = media_fetcher.generate_professional_thumbnail(
            keyword=thumb_keyword,
            hook_text=hook_text,
            output_stem=stem
        )
    except Exception as thumb_err:
        logger.error(f"⚠️ Thumbnail engine skipped due to safe intercept rule: {thumb_err}")

    # STEP 3: Voiceover Audio Synthesis
    logger.info("STEP 3/5 — Generating voiceover synthesis…")
    voiceover_data = audio_generator.generate_voiceover(
        script      = script_data.get("script", ""),
        output_stem = stem,
    )

    # STEP 4: Compile Final Video
    logger.info("STEP 4/5 — Rendering high-retention video composition with MoviePy…")
    video_path = video_compiler.compile_video(
        media_paths    = media_paths,
        voiceover_data = voiceover_data,
        output_stem    = stem,
    )
    logger.info(f"Video composition compiled successfully → {video_path}")

    # STEP 5: Upload
    upload_results = {}
    if not skip_upload:
        logger.info("STEP 5/5 — Dispatching multi-platform cloud upload sequences…")
        
        upload_results = uploader.upload_all_platforms(
            video_path     = video_path,
            seo            = script_data.get("seo", {}),
            thumbnail_path = thumbnail_path,
        )
        if upload_results and "success" in str(upload_results.get("youtube", "")):
            _log_upload(stem, upload_results)
            logger.info("✅ Upload logged for duplicate prevention.")
    else:
        logger.info("STEP 5/5 — Upload skipped (--skip-upload active).")

    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"✅ Anti-Spam Pipeline safely completed in {elapsed:.1f}s")
    logger.info("=" * 60)

    return {
        "stem":           stem,
        "video_path":     video_path,
        "seo":            script_data.get("seo", {}),
        "upload_results": upload_results,
        "thumbnail_path": thumbnail_path
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Dark Realities Video Pipeline")
    parser.add_argument("--topic",       type=str,  default=None, help="Override topic keyword")
    parser.add_argument("--skip-upload", action="store_true",      help="Render locally only")
    args = parser.parse_args()

    run_pipeline(topic=args.topic, skip_upload=args.skip_upload)
