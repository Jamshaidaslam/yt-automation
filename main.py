import os
import sys
import logging
import requests
import argparse
from pathlib import Path

# FIX: PIL Attribute Error (ANTIALIAS issue)
from PIL import Image
try:
    getattr(Image, 'Resampling')
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    Image.ANTIALIAS = Image.LANCZOS

from script_generator import generate_script, pick_topic_for_run
from audio_generator import generate_voiceover
from video_compiler import compile_final_video

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

MEDIA_CACHE_DIR = Path("output/media")
FINAL_OUTPUT_DIR = Path("output/final_videos")

def clean_production_environment():
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def download_live_pexels_broll(scenes: list) -> list:
    logger.info("🌐 Fetching B-roll from Pexels...")
    api_key = os.getenv("PEXELS_API_KEY")
    downloaded_paths = []
    headers = {"Authorization": api_key} if api_key else {}

    for idx, scene in enumerate(scenes):
        query = scene.get("visual_query", "dark psychology")
        clip_path = MEDIA_CACHE_DIR / f"broll_scene_{idx+1}.mp4"
        
        success = False
        if api_key:
            url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page=5&orientation=portrait"
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    videos = response.json().get("videos", [])
                    if videos:
                        video_files = videos[0].get("video_files", [])
                        # Force download high quality
                        target_file = video_files[0]
                        os.system(f'curl -L -s -o "{clip_path}" "{target_file["link"]}"')
                        if clip_path.exists() and clip_path.stat().st_size > 5000:
                            downloaded_paths.append(str(clip_path))
                            logger.info(f"✅ Clip {idx+1} downloaded: {query}")
                            success = True
            except Exception as e:
                logger.warning(f"⚠️ Pexels fetch error: {e}")

        if not success:
            logger.info(f"🔄 Using backup clip for: {query}")
            os.system(f'ffmpeg -y -f lavfi -i testsrc=duration=5:size=1080x1920:rate=30 -c:v libx264 -pix_fmt yuv420p "{clip_path}" > /dev/null 2>&1')
            downloaded_paths.append(str(clip_path))

    return downloaded_paths

def execute_pipeline(topic: str = ""):
    logger.info("🔥 Starting Automated Video Pipeline...")
    try:
        if not topic:
            topic = pick_topic_for_run()
            logger.info(f"🔄 Auto-selected topic: {topic}")
        
        clean_production_environment()

        # 1. Script
        script_data = generate_script(topic)

        # 2. Voiceover
        voiceover_payload = generate_voiceover(
            script_data["voiceover"],
            "temp_voice_stream",
            voice_type="guy_dark"
        )

        # 3. B-Roll
        video_clips_paths = download_live_pexels_broll(script_data.get("scenes", []))
        
        # 4. Compile
        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        compile_final_video(video_clips_paths, voiceover_payload, "", str(output_video_file))

        if output_video_file.exists():
            logger.info(f"✨ Pipeline finished successfully! Video saved at: {output_video_file}")
        else:
            raise Exception("Compilation failed - output file not created.")

    except Exception:
        logger.critical("🚨 PIPELINE CRASHED!", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args = parser.parse_args()
    execute_pipeline(args.topic.strip())
