"""
main.py — YouTube Automation Pipeline
"""

import os, logging, random, sys, shutil
from pathlib import Path
from script_generator import generate_script
from audio_generator import generate_voiceover
from media_fetcher import fetch_broll_clips
from video_compiler import compile_final_video

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

MEDIA_CACHE_DIR  = Path("output/media")
FINAL_OUTPUT_DIR = Path("output/final_videos")


def clean_and_prep():
    if MEDIA_CACHE_DIR.exists():
        shutil.rmtree(MEDIA_CACHE_DIR)
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def execute_pipeline(topic: str):
    logger.info(f"🚀 Pipeline starting for: {topic}")

    clean_and_prep()

    # 1. Script
    logger.info("📝 Generating script...")
    script_data = generate_script(topic)
    if not script_data or not script_data.get("voiceover"):
        logger.critical("❌ Script generation failed — empty voiceover text.")
        sys.exit(1)

    # 2. Voiceover
    logger.info("🎙  Generating voiceover...")
    voice_data = generate_voiceover(script_data["voiceover"], "main_voice")
    if not voice_data or not voice_data.get("audio_path"):
        logger.critical("❌ Voiceover generation failed.")
        sys.exit(1)
    if not os.path.exists(voice_data["audio_path"]):
        logger.critical(f"❌ Audio file not found: {voice_data['audio_path']}")
        sys.exit(1)

    # 3. B-Roll Clips
    # 20+ clips * 2s fast cut = 40-55s video (hits 35-55s target)
    logger.info("🎞  Fetching B-roll clips...")
    visual_queries = script_data.get(
        "visual_queries",
        ["dark atmosphere", "minimalist", "high status lifestyle"]
    )
    video_paths = fetch_broll_clips(visual_queries, clips_per_keyword=10)
    if not video_paths:
        logger.critical("❌ No video clips fetched. Check media_fetcher.")
        sys.exit(1)
    logger.info(f"✅ {len(video_paths)} clips ready.")

    # 4. Compile
    logger.info("🎬 Compiling final video...")
    output_path  = FINAL_OUTPUT_DIR / "final_output.mp4"
    bgm_path     = "assets/music/dark.mp3"
    title_text   = script_data.get("title", topic)

    result = compile_final_video(
        video_clips_paths=video_paths,
        voiceover_data=voice_data,
        bgm_file_path=bgm_path,
        output_path=str(output_path),
        title_text=title_text,
    )

    # compile_final_video returns (video_path, thumbnail_path)
    if isinstance(result, tuple):
        final_video_path, thumbnail_path = result
    else:
        final_video_path = result
        thumbnail_path   = None

    # 5. Verify output
    if not os.path.exists(final_video_path):
        logger.critical(f"❌ Output video not found at: {final_video_path}")
        sys.exit(1)

    size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
    logger.info(f"✅ Video ready  → {final_video_path}  ({size_mb:.1f} MB)")
    if thumbnail_path:
        logger.info(f"🖼  Thumbnail   → {thumbnail_path}")

    return final_video_path, thumbnail_path


if __name__ == "__main__":
    pool = [
        "How to use the Half-Sentence Trap to make her obsess over you",
        "The silent sub-cue that makes people instantly submit to your status",
        "How to read a woman's true intentions in under 3 seconds",
        "The psychological pause that forces authority in any room",
        "Why being 'too available' kills your attraction and how to fix it"
    ]

    topic = random.choice(pool)
    execute_pipeline(topic)
