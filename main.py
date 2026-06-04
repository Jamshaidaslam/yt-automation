"""
main.py — Master Automation Executive Workflow (PRODUCTION ENGINE v3.5 - BUG FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fixes:
  1. media_fetcher import added
  2. Keywords extracted from script scenes
  3. --skip-upload flag implemented
  4. BGM download: os.system curl replaced with requests.get
  5. BGM timeout 30→15, multiple fallback URLs added (Mixkit GitHub Actions pe block hota tha)
"""

import os
import shutil
import logging
import requests
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


def dynamic_auto_music_downloader(topic: str) -> str:
    local_bgms = list(BGM_INPUT_DIR.glob("*.mp3")) + list(BGM_INPUT_DIR.glob("*.wav"))
    if local_bgms:
        logger.info("🎵 Using existing local background music file asset.")
        return str(local_bgms[0])

    target_track_path = BGM_INPUT_DIR / "dynamic_scraped_bgm.mp3"

    if target_track_path.exists():
        try:
            target_track_path.unlink()
        except Exception:
            pass

    # FIX: Multiple fallback URLs — Mixkit GitHub Actions pe block hota tha
    # FIX: timeout 30 → 15 — pehle 30 sec wait karta tha har URL pe, isliye 7 min lag rahe the
    bgm_urls = [
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    ]

    for bgm_url in bgm_urls:
        try:
            logger.info(f"📥 Downloading BGM from: {bgm_url}")
            response = requests.get(bgm_url, timeout=15, stream=True)
            if response.status_code == 200:
                with open(target_track_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                if target_track_path.exists() and target_track_path.stat().st_size > 30000:
                    logger.info(f"✅ BGM downloaded. Size: {target_track_path.stat().st_size} bytes")
                    return str(target_track_path)
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ BGM URL timed out: {bgm_url} — trying next...")
        except Exception as e:
            logger.warning(f"⚠️ BGM download failed ({bgm_url}): {e} — trying next...")

    logger.warning("⚠️ All BGM URLs failed. Proceeding without background music.")
    return ""


def engineer_clickbait_title(raw_title: str) -> str:
    clean_title = raw_title.replace('"', "").strip()
    if not clean_title.endswith("..."):
        clean_title += "..."
    return f"🧠 {clean_title} #darkpsychology #manipulation #shorts"


def execute_pipeline(topic: str, skip_upload: bool = False):
    logger.info("🔥 Activating Automated Dark Realities Script Sequence Pipeline...")
    try:
        clean_production_environment()

        # STEP 1: Generate script
        script_data = generate_script(topic)
        engineered_title = engineer_clickbait_title(script_data.get("title", "The Dark Truth"))
        logger.info(f"🎯 Production Title: {engineered_title}")

        # STEP 2: Generate voiceover
        voiceover_payload = generate_voiceover(
            script_data["voiceover"], "temp_voice_stream", voice_type="guy_dark"
        )

        # STEP 3: Extract keywords from scenes
        scenes = script_data.get("scenes", [])
        keywords = [
            scene.get("visual_query", "").strip()
            for scene in scenes
            if scene.get("visual_query", "").strip()
        ]
        if not keywords:
            keywords = [topic]

        # STEP 4: Fetch B-roll clips
        video_clips_paths = fetch_broll_clips(keywords, clips_per_keyword=2)
        if not video_clips_paths:
            raise RuntimeError("Media engine returned zero clips. Check API keys.")

        # STEP 5: Download BGM
        resolved_bgm_path = dynamic_auto_music_downloader(topic)

        # STEP 6: Compile video
        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        compile_final_video(
            video_clips_paths, voiceover_payload, resolved_bgm_path, str(output_video_file)
        )

        if not output_video_file.exists() or output_video_file.stat().st_size == 0:
            raise FileNotFoundError("Render completed but output file is missing or empty.")

        logger.info(f"✨ PIPELINE SUCCESSFUL. Output size: {output_video_file.stat().st_size} bytes")

        # STEP 7: Upload
        if skip_upload:
            logger.info("⏭️ Upload step skipped (--skip-upload flag active).")
        else:
            seo = {
                "title": engineered_title,
                "description": script_data.get("voiceover", "")[:200],
                "hashtags": ["#DarkPsychology", "#Mindset", "#Shorts", "#darkfacts"]
            }
            from media_fetcher import generate_professional_thumbnail
            thumbnail_path = generate_professional_thumbnail(
                keywords[0],
                script_data.get("title", "Dark Truth"),
                "main_thumb"
            )
            upload_results = upload_all_platforms(
                str(output_video_file), seo, thumbnail_path=thumbnail_path
            )
            logger.info(f"📤 Upload Results: {upload_results}")

    except Exception as pipeline_error:
        logger.critical("🚨 PIPELINE CRASHED!", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    parser.add_argument("--skip-upload", action="store_true", help="Render only, do not upload.")
    args = parser.parse_args()

    target_topic = (
        args.topic.strip()
        if args.topic.strip()
        else "How your phone uses dark psychology as a dopamine trap"
    )
    execute_pipeline(target_topic, skip_upload=args.skip_upload)
