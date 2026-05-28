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
    stem       = f"ai_dark_{timestamp}"

    logger.info("=" * 60)
    logger.info(f"🎬  AI Dark Realities Pipeline  |  {timestamp}")
    logger.info("=" * 60)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Script + SEO generation
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("STEP 1/5 — Generating script via Groq…")
    script_data = script_generator.generate_script(topic)

    # Persist script JSON for audit / re-runs
    script_path = config.SCRIPTS_DIR / f"{stem}_script.json"
    script_path.write_text(json.dumps(script_data, indent=2), encoding="utf-8")
    logger.info(f"Script saved → {script_path.name}")
    logger.info(f"Title: {script_data['seo']['title']}")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: B-roll media download
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("STEP 2/5 — Fetching B-roll media…")
    broll_paths = media_fetcher.fetch_broll_clips(
        keywords         = script_data["broll_keywords"],
        clips_per_keyword= config.MEDIA_PER_KEYWORD,
    )

    if not broll_paths:
        logger.error("No B-roll clips retrieved — aborting pipeline.")
        sys.exit(1)

    logger.info(f"B-roll ready: {len(broll_paths)} clips")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Voiceover synthesis
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("STEP 3/5 — Synthesising voiceover via Edge-TTS…")
    audio_meta = audio_generator.generate_voiceover(
        script      = script_data["script"],
        output_stem = stem,
    )
    logger.info(f"Audio duration: {audio_meta['duration_sec']:.2f}s")

    # Validate duration is within target range
    dur = audio_meta["duration_sec"]
    if dur < config.MIN_DURATION_SEC:
        logger.warning(f"Audio is {dur:.1f}s — shorter than {config.MIN_DURATION_SEC}s target.")
    elif dur > config.MAX_DURATION_SEC:
        logger.warning(f"Audio is {dur:.1f}s — longer than {config.MAX_DURATION_SEC}s target.")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: Video compilation
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("STEP 4/5 — Compiling video…")
video_path = video_compiler.compile_video(
    media_paths     = media_paths,  
    voiceover_data  = voiceover_data,
    output_stem     = stem,
)
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
            seo        = script_data["seo"],
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
        "seo":            script_data["seo"],
        "upload_results": upload_results,
    }


# ── CLI entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Dark Realities Video Pipeline")
    parser.add_argument("--topic",       type=str,  default=None,  help="Override topic (optional)")
    parser.add_argument("--skip-upload", action="store_true",       help="Render only, skip posting")
    args = parser.parse_args()

    result = run_pipeline(topic=args.topic, skip_upload=args.skip_upload)
    print(json.dumps(result, indent=2, default=str))
