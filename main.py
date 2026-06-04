"""
main.py — Master Automation Executive Workflow (NEURAL INFLUENCE INTEGRATION v4.0)
AI Influence Warfare · 100% FREE Short-Form Video Pipeline
Upgrades:
  1. Dynamic Niche Broadener: Auto-rotates across Eye-Reading, Alpha Status, and Attraction Codes.
  2. Algorithm Bypass Fingerprint Masking: Auto-shuffles title tags & voice profile anchors.
  3. Safe-SEO Mapping: Avoids shadowban words inside hashtags/metadata.
"""

import os
import shutil
import logging
import requests
import random
import sys
from pathlib import Path
from script_generator import generate_script
from audio_generator import generate_voiceover
from media_fetcher import fetch_broll_clips
from video_compiler import compile_final_video
from uploader import upload_all_platforms

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

MEDIA_CACHE_DIR = Path("output/media")
FINAL_OUTPUT_DIR = Path("output/final_videos")
BGM_INPUT_DIR = Path("assets/bgm")


def clean_production_environment():
    logger.info("🧹 Performing complete media cache clean reset...")
    if MEDIA_CACHE_DIR.exists():
        shutil.rmtree(MEDIA_CACHE_DIR)
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BGM_INPUT_DIR.mkdir(parents=True, exist_ok=True)


def dynamic_auto_music_downloader() -> str:
    """Selects local background scores dynamically from assets."""
    for search_dir in [BGM_INPUT_DIR, Path("assets/music")]:
        if search_dir.exists():
            tracks = (
                list(search_dir.glob("*.mp3")) +
                list(search_dir.glob("*.wav")) +
                list(search_dir.glob("*.m4a"))
            )
            if tracks:
                chosen = random.choice(tracks)
                logger.info(f"🎵 Local BGM loaded: {chosen.name}")
                return str(chosen)

    logger.warning("⚠️ No local BGM found in assets directories. Proceeding without ambient score.")
    return ""


def engineer_clickbait_title(raw_title: str) -> str:
    """Engineers high-CTR clickbait tags optimized for USA/UK hooks."""
    clean_title = raw_title.replace('"', "").strip()
    if not clean_title.endswith("..."):
        clean_title += "..."
        
    # 🔥 ALGORITHM BYPASS: Shuffling dynamic safe tags instead of hardcoded manipulation words
    tag_sets = [
        ["#mindcontrol", "#humanpsychology", "#shorts", "#readpeople"],
        ["#bodylanguage", "#statusmove", "#psychologytricks", "#viral"],
        ["#subconsciousmind", "#influence", "#shorts", "#wisdomcodes"]
    ]
    selected_tags = " ".join(random.choice(tag_sets))
    return f"🧠 {clean_title} {selected_tags}"


def execute_pipeline(topic: str, skip_upload: bool = False):
    logger.info("🔥 Activating Automated Neural Influence Pipeline Sequence...")
    try:
        clean_production_environment()

        # STEP 1: Generate high-retention script blueprint
        script_data = generate_script(topic)
        engineered_title = engineer_clickbait_title(script_data.get("title", "The Unspoken Code"))
        logger.info(f"🎯 Production Title: {engineered_title}")

        # STEP 2: Generate dynamic voiceover with automated fingerprint rotation
        voice_profile = random.choice(["guy_dark", "ryan_uk"])
        logger.info(f"🎙️ Assigning dynamic voice model anchor: [{voice_profile}]")
        
        voiceover_payload = generate_voiceover(
            script_data["voiceover"], "temp_voice_stream", voice_type=voice_profile
        )

        # STEP 3: Extract keywords from cinematic scenes
        scenes = script_data.get("scenes", [])
        keywords = [
            scene.get("visual_query", "").strip()
            for scene in scenes
            if scene.get("visual_query", "").strip()
        ]
        if not keywords:
            keywords = [topic]

        # STEP 4: Fetch fast-cutting B-roll assets based on keywords
        video_clips_paths = fetch_broll_clips(keywords, clips_per_keyword=2)
        if not video_clips_paths:
            raise RuntimeError("Media fetcher engine returned zero clips. Validation failed.")

        # STEP 5: Assign local music layers
        resolved_bgm_path = dynamic_auto_music_downloader()

        # STEP 6: Compile cinematic video with dynamic slow zooms
        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        compile_final_video(
            video_clips_paths, voiceover_payload, resolved_bgm_path, str(output_video_file)
        )

        if not output_video_file.exists() or output_video_file.stat().st_size == 0:
            raise FileNotFoundError("Render layer pipeline completed but final file footprint is empty.")

        logger.info(f"✨ PIPELINE SUCCESSFUL. Output size: {output_video_file.stat().st_size} bytes")

        # STEP 7: Automated Multi-Platform Deployment
        if skip_upload:
            logger.info("⏭️ Upload step skipped (--skip-upload flag active).")
        else:
            seo = {
                "title": engineered_title,
                "description": script_data.get("voiceover", "")[:200],
                "hashtags": ["#MindControl", "#ReadPeople", "#Shorts", "#Subconscious"]
            }
            from media_fetcher import generate_professional_thumbnail
            thumbnail_path = generate_professional_thumbnail(
                keywords[0],
                script_data.get("title", "Influence Code"),
                "main_thumb"
            )
            upload_results = upload_all_platforms(
                str(output_video_file), seo, thumbnail_path=thumbnail_path
            )
            logger.info(f"📤 Upload Matrix Deploy Results: {upload_results}")

    except Exception as pipeline_error:
        logger.critical("🚨 PRODUCTION PIPELINE CRASHED!", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    parser.add_argument("--skip-upload", action="store_true", help="Render only, do not upload.")
    args = parser.parse_args()

    # 🔥 VIRAL POOL ROTATION: If no specific topic passed, automatic choice from elite categories
    viral_fallback_pool = [
        "How to read someone's true intentions just by watching their eyes",
        "The subconscious body language trick to make anyone instantly respect your status",
        "How to control any room you walk into without saying a single word",
        "The psychological pause that forces loud people to stop and listen to you",
        "How to use reverse psychology on a difficult person to get exactly what you want",
        "How to look into someone's left eye to detect if they are hiding a truth from you",
        "The subconscious loop behavior to keep your presence on their mind all day long",
        "How elite high-status leaders secretly dominate a conversation using silent sub-cues"
    ]

    target_topic = args.topic.strip()
    if not target_topic:
        target_topic = random.choice(viral_fallback_pool)
        logger.info(f"🎲 Topic pool selected random blueprint: [{target_topic}]")

    execute_pipeline(target_topic, skip_upload=args.skip_upload)
