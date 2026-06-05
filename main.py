import os
import json
import logging
import requests
import sys
from pathlib import Path

# Fix: Import pick_topic_for_run
from script_generator import generate_script, pick_topic_for_run
from audio_generator import generate_voiceover
from video_compiler import compile_final_video
from uploader_youtube import upload_to_youtube
from uploader_instagram import upload_to_instagram

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

MEDIA_CACHE_DIR = Path("output/media")
FINAL_OUTPUT_DIR = Path("output/final_videos")
BGM_INPUT_DIR = Path("assets/bgm")

def clean_production_environment():
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BGM_INPUT_DIR.mkdir(parents=True, exist_ok=True)

def download_live_pexels_broll(scenes: list) -> list:
    logger.info("🌐 Fetching B-roll from Pexels...")
    api_key = os.getenv("PEXELS_API_KEY")
    downloaded_paths = []
    headers = {"Authorization": api_key} if api_key else {}

    for idx, scene in enumerate(scenes):
        # Yahan visual_query sahi key hai
        query = scene.get("visual_query", "dark psychology")
        clip_path = MEDIA_CACHE_DIR / f"broll_scene_{idx+1}.mp4"
        success = False

        if api_key:
            url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page=3&orientation=portrait"
            try:
                response = requests.get(url, headers=headers, timeout=12)
                if response.status_code == 200:
                    videos = response.json().get("videos", [])
                    if videos:
                        video_files = videos[0].get("video_files", [])
                        hd_files = [f for f in video_files if f.get("quality") == "hd" or f.get("width", 0) >= 720]
                        target_file = hd_files[0] if hd_files else (video_files[0] if video_files else None)
                        if target_file:
                            os.system(f'curl -L -s -o "{clip_path}" "{target_file["link"]}"')
                            if clip_path.exists() and clip_path.stat().st_size > 40000:
                                downloaded_paths.append(str(clip_path))
                                success = True
            except: pass

        if not success:
            try:
                os.system(f'ffmpeg -y -f lavfi -i testsrc=duration=4:size=1080x1920:rate=30 -vf "hue=H=2*PI*t:s=0.4" -c:v libx264 -pix_fmt yuv420p "{clip_path}" > /dev/null 2>&1')
                if clip_path.exists(): downloaded_paths.append(str(clip_path))
            except: pass
    return downloaded_paths

def execute_pipeline(topic: str = ""):
    logger.info("🔥 Starting Automated Video Pipeline...")
    try:
        # FIX: Agar topic nahi diya gaya, to random pick karo
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

        # 3. B-Roll (Matches "scenes" key from script_generator)
        video_clips_paths = download_live_pexels_broll(script_data.get("scenes", []))
        
        # 4. Compile
        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        compile_final_video(video_clips_paths, voiceover_payload, "", str(output_video_file))

        if not (output_video_file.exists()):
            raise FileNotFoundError("Render failed.")

        logger.info("✨ Pipeline finished successfully!")

    except Exception:
        logger.critical("🚨 PIPELINE CRASHED!", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args = parser.parse_args()
    execute_pipeline(args.topic.strip())
