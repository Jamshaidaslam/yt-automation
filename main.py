"""
main.py — Pipeline Orchestrator (ANTI-SPAM & INTENT ALIGNED v2.5)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import argparse
import json
import logging
import sys
import time
import os
from datetime import datetime
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

def run_pipeline(topic: str | None = None, skip_upload: bool = False) -> dict:
    start_time = time.time()
    # Pacing Control: Meta platforms like exact naming structures
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem       = f"video_{timestamp}"

    logger.info("=" * 60)
    logger.info(f"🚀 STARTING ANTI-SPAM PIPELINE SESSION: {stem.upper()}")
    logger.info("=" * 60)

    # STEP 1: Script Generation
    logger.info("STEP 1/5 — Invoking Groq LLM for script engineering…")
    script_data = script_generator.generate_script(topic=topic)
    script_output = SCRIPTS_DIR / f"{stem}.json"
    script_output.write_text(json.dumps(script_data, indent=2), encoding="utf-8")

    # STEP 2: Media Asset Procurement (CRITICAL BUG FIX: Precise Key Alignment)
    logger.info("STEP 2/5 — Querying stock video download engines…")
    
    # Strictly fetch the highly cinematic broll keywords from our system prompt
    keywords_list = script_data.get("broll_keywords") or script_data.get("search_keywords") or script_data.get("keywords")
    
    # Safe validation layer to prevent dummy words like ("the", "is", "or") being searched
    if not keywords_list or not isinstance(keywords_list, list) or len(keywords_list) == 0:
        logger.warning("Groq dynamic key failed or returned empty list. Injecting high-retention fallbacks.")
        keywords_list = [
            "dark aesthetic cinematic", 
            "mysterious silhouette shadow", 
            "brain neural activity glow", 
            "closeup eye fear thriller"
        ]

    logger.info(f"Targeting visual database with clean intents: {keywords_list}")
    media_paths = media_fetcher.fetch_broll_clips(
        keywords          = keywords_list,
        clips_per_keyword = MEDIA_PER_KEYWORD,
    )

    if not media_paths:
        logger.error("Pipeline failure: Visual database denied access or no B-roll fetched.")
        sys.exit(1)

    # STEP 3: Voiceover Audio Synthesis
    logger.info("STEP 3/5 — Generating voiceover synthesis…")
    voiceover_data = audio_generator.generate_voiceover(
        script      = script_data.get("script", ""),
        output_stem = stem,
    )

    # STEP 4: Compile Final Video
    logger.info("STEP 4/5 — Rendering high-retention video composition with MoviePy…")
    video_path = video_compiler.compile_video(
        media_paths     = media_paths,
        voiceover_data  = voiceover_data,
        output_stem     = stem,
    )
    logger.info(f"Video composition compiled successfully → {video_path}")

    # STEP 5: Secure Multi-Platform Upload Stream
    upload_results = {}
    if not skip_upload:
        logger.info("STEP 5/5 — Dispatching multi-platform cloud upload sequences…")
        upload_results = uploader.upload_all_platforms(
            video_path = video_path,
            seo        = script_data.get("seo", {}),
        )
    else:
        logger.info("STEP 5/5 — Upload protocol skipped (--skip-upload active).")

    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"✅ Anti-Spam Pipeline safely completed in {elapsed:.1f}s")
    logger.info("=" * 60)

    return {
        "stem":           stem,
        "video_path":      video_path,
        "seo":            script_data.get("seo", {}),
        "upload_results": upload_results,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Dark Realities Video Pipeline")
    parser.add_argument("--topic",       type=str,  default=None,  help="Override topic keyword")
    parser.add_argument("--skip-upload", action="store_true",       help="Render asset locally only")
    args = parser.parse_args()

    run_pipeline(topic=args.topic, skip_upload=args.skip_upload)
