"""
main.py — Master Automation Executive Workflow (PRODUCTION ENGINE v4.0 - FULL SCALE TIMINGS)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import shutil
import logging
import requests
import sys
import re
from pathlib import Path

# Hotfix layer matrix for Pillow compatibility tracking
import PIL
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from script_generator import generate_script
from audio_generator import generate_voiceover
from video_compiler import compile_final_video

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

def download_live_pexels_broll(scenes: list) -> list:
    logger.info("🌐 Activating live Pexels API media scraper engine...")
    api_key = os.getenv("PEXELS_API_KEY")
    downloaded_paths = []

    headers = {"Authorization": api_key} if api_key else {}

    for idx, scene in enumerate(scenes):
        query = scene.get("visual_query", "dark psychology")
        clip_path = MEDIA_CACHE_DIR / f"broll_scene_{idx+1}.mp4"
        success = False

        if api_key:
            logger.info(f"🔍 Searching Pexels for Clip [{idx+1}]: '{query}'")
            url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page=5&orientation=portrait"
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    videos = response.json().get("videos", [])
                    if videos:
                        video_files = videos[0].get("video_files", [])
                        hd_files = [f for f in video_files if f.get("quality") == "hd" or f.get("width", 0) >= 720]
                        target_file = hd_files[0] if hd_files else (video_files[0] if video_files else None)
                        
                        if target_file:
                            download_url = target_file["link"]
                            os.system(f'curl -L -s -o "{clip_path}" "{download_url}"')
                            if clip_path.exists() and clip_path.stat().st_size > 50000:
                                downloaded_paths.append(str(clip_path))
                                logger.info(f"✅ Downloaded live clip: {clip_path}")
                                success = True
            except Exception as e:
                logger.error(f"❌ Pexels download failed on scene [{idx+1}]: {e}")

        if not success:
            logger.warning(f"⚠️ Falling back to high-retention structural base loop for scene [{idx+1}]")
            try:
                os.system(f'ffmpeg -y -f lavfi -i testsrc=duration=7:size=1080x1920:rate=30 -vf "hue=H=2*PI*t:s=0.3" -c:v libx264 -pix_fmt yuv420p "{clip_path}" > /dev/null 2>&1')
                if clip_path.exists():
                    downloaded_paths.append(str(clip_path))
            except Exception as ffmpeg_err:
                logger.error(f"❌ Failed to generate local asset loop: {ffmpeg_err}")

    return downloaded_paths

def dynamic_auto_music_downloader(topic: str) -> str:
    local_bgms = list(BGM_INPUT_DIR.glob("*.mp3")) + list(BGM_INPUT_DIR.glob("*.wav"))
    if local_bgms: return str(local_bgms[0])
    target_track_path = BGM_INPUT_DIR / "dynamic_scraped_bgm.mp3"
    static_url = "https://assets.mixkit.co/music/preview/mixkit-glitchy-futuristic-ambient-mystery-1149.mp3"
    try:
        os.system(f'curl -L -s -o "{target_track_path}" "{static_url}"')
        if target_track_path.exists(): return str(target_track_path)
    except: pass
    return ""

def execute_pipeline(topic: str):
    logger.info("🔥 Activating Automated Dark Realities Script Sequence Pipeline...")
    try:
        clean_production_environment()

        script_data = generate_script(topic)
        voiceover_payload = generate_voiceover(script_data["voiceover"], "temp_voice_stream", voice_type="guy_dark")

        video_clips_paths = download_live_pexels_broll(script_data["scenes"])
        resolved_bgm_path = dynamic_auto_music_downloader(topic)

        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        compile_final_video(video_clips_paths, voiceover_payload, resolved_bgm_path, str(output_video_file))

        if output_video_file.exists() and output_video_file.stat().st_size > 0:
            logger.info("✨ PIPELINE EXECUTION SUCCESSFUL.")
        else:
            raise FileNotFoundError("Render payload missing.")

    except Exception as pipeline_error:
        logger.critical("🚨 PIPELINE CRASHED INSIDE MASTER RUN LAYER!", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args = parser.parse_args()
    target_topic = args.topic if args.topic.strip() else "How your phone uses dark psychology as a dopamine trap"
    execute_pipeline(target_topic)
