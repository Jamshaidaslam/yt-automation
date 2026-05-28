"""
main.py — Pipeline Orchestrator
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
Runs the complete end-to-end pipeline for ONE video:
  1. Generate script + SEO via Groq
  2. Download B-roll media (Pexels → Pixabay fallback)
  3. Synthesise Edge-TTS voiceover
  4. Compile final vertical MP4 with captions + motion
  5. Upload to all configured platforms

Called by GitHub Actions (one run per cron trigger = one video per day slot).
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import config
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
    """
    Execute the full video creation + posting pipeline.

    Parameters
    ----------
    topic       : str | None — force a specific topic (None = random)
    skip_upload : bool       — render video but don't post (useful for testing)

    Returns
    -------
    dict — summary of the run {stem, video_path, seo, upload_results}
    """
    start_time = time.time()
    timestamp  = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stem       = f"video_{timestamp}"

    logger.info("=" * 60)
    logger.info(f"🚀 Starting Pipeline Session: {stem.upper()}")
    if topic:
        logger.info(f"🎯 Target Topic Forced: '{topic}'")
    logger.info("=" * 60)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Script + SEO generation via Groq Cloud
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("STEP 1/5 — Invoking Groq LLM for script engineering…")
    script_data = script_generator.generate_script(topic=topic)
    
    # Save script JSON metadata for archive transparency
    script_output = config.SCRIPTS_DIR / f"{stem}.json"
    script_output.write_text(json.dumps(script_data, indent=2), encoding="utf-8")
    
    logger.info(f"Script generated successfully -> {script_output.name}")
    logger.info(f"Title: {script_data.get('seo', {}).get('title', 'Untitled')}")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Media Asset Procurement (B-Roll Video Clips)
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("STEP 2/5 — Querying stock video download engines…")
    
    # FIX: KeyError se bachne ke liye alternate keys extraction aur automatic fallback check
    keywords_list = script_data.get("search_keywords") or script_data.get("keywords") or script_data.get("broll_keywords")
    
    if not keywords_list:
        title_text = script_data.get("seo", {}).get("title", "dark secrets mystery")
        keywords_list = [w.strip() for w in title_text.split() if len(w) > 3][:3]
        logger.warning(f"Groq API response missing search keys. Generated fallbacks: {keywords_list}")

    media_paths = media_fetcher.fetch_broll_clips(
        keywords          = keywords_list,
        clips_per_keyword = config.MEDIA_PER_KEYWORD,
    )

    if not media_paths:
        logger.error("Pipeline failure: No B-roll visual assets could be fetched.")
        sys.exit(1)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Voiceover Audio Synthesis + Subtitle Timings
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("STEP 3/5 — Generating natural TTS voice synthesis…")
    voiceover_data = audio_generator.generate_voiceover(
        script      = script_data.get("script", ""),
        output_stem = stem,
    )

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: Compile final vertical video with captions
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("STEP 4/5 — Rendering video composition with MoviePy…")
    video_path = video_compiler.compile_video(
        media_paths     = media_paths,
        voiceover_data  = voiceover_data,
        output_stem     = stem,
    )
    logger.info(f"Video ready → {video_path}")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5: Multi-platform upload
    # ─────────────────────────────────────────────────────────────────────────
    upload_results = {}
    if not skip_upload:
        logger.info("STEP 5/5 — Uploading to all platforms…")
        upload_results = uploader.upload_all_platforms(
            video_path = video_path,
            seo        = script_data.get("seo", {}),
        )
    else:
        logger.info("STEP 5/5 — Upload skipped (--skip-upload flag).")

    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"✅  Pipeline complete in {elapsed:.1f}s")
    logger.info("=" * 60)

    return {
        "stem":           stem,
        "video_path":     video_path,
        "seo":            script_data.get("seo", {}),
        "upload_results": upload_results,
    }


# ── CLI entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Dark Realities Video Pipeline")
    parser.add_argument("--topic",       type=str,  default=None,  help="Override topic (optional)")
    parser.add_argument("--skip-upload", action="store_true",       help="Render only, skip posting")
    args = parser.parse_args()

    result = run_pipeline(topic=args.topic, skip_upload=args.skip_upload)
