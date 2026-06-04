"""
main.py — Master Automation Executive Workflow (PRODUCTION ENGINE v3.4 - MUSIC ENGINE FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fixed: Re-engineered dynamic downloader to prevent 1134-byte corruption bugs on GitHub runners.
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import shutil
import logging
import requests
import sys
from pathlib import Path
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
    if not api_key:
        logger.warning("⚠️ PEXELS_API_KEY missing!")
        return []

    downloaded_paths = []
    headers = {"Authorization": api_key}

    for idx, scene in enumerate(scenes):
        query = scene.get("visual_query", "dark psychology")
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
                        clip_path = MEDIA_CACHE_DIR / f"broll_scene_{idx+1}.mp4"
                        os.system(f'curl -L -s -o "{clip_path}" "{download_url}"')
                        if clip_path.exists() and clip_path.stat().st_size > 100000:
                            downloaded_paths.append(str(clip_path))
                            logger.info(f"✅ Downloaded clip saved: {clip_path}")
        except Exception as e:
            logger.error(f"❌ Scraper failure on scene [{idx+1}]: {e}")
    return downloaded_paths

def dynamic_auto_music_downloader(topic: str) -> str:
    """
    🎵 FIXED STATIC PREMIUM MUSIC LINK NODE
    Bypasses unstable Pixabay API streams to prevent corrupt file generations.
    """
    local_bgms = list(BGM_INPUT_DIR.glob("*.mp3")) + list(BGM_INPUT_DIR.glob("*.wav"))
    if local_bgms:
        logger.info("🎵 Using existing local background music file asset.")
        return str(local_bgms[0])

    target_track_path = BGM_INPUT_DIR / "dynamic_scraped_bgm.mp3"
    
    # Clean previous corrupt residual logs if any exist
    if target_track_path.exists():
        try: target_track_path.unlink()
        except: pass

    logger.info("📥 Downloading verified Premium Suspense Background score via native curl pipe...")
    # Direct high-speed CDN node that never returns 1134 bytes errors
    static_url = "https://assets.mixkit.co/music/preview/mixkit-glitchy-futuristic-ambient-mystery-1149.mp3"
    
    try:
        os.system(f'curl -L -s -o "{target_track_path}" "{static_url}"')
        if target_track_path.exists() and target_track_path.stat().st_size > 30000:
            logger.info(f"✅ Premium background track loaded successfully! Size: {target_track_path.stat().st_size} bytes")
            return str(target_track_path)
    except Exception as e:
        logger.error(f"❌ Audio stream pipe down: {e}")

    logger.critical("🚨 Safe-valve active. Compiling pure narrative print.")
    return ""

def engineer_clickbait_title(raw_title: str) -> str:
    clean_title = raw_title.replace('"', '').strip()
    if not clean_title.endswith("..."):
        clean_title += "..."
    return f"🧠 {clean_title} #darkpsychology #manipulation #shorts"

def execute_pipeline(topic: str):
    logger.info("🔥 Activating Automated Dark Realities Script Sequence Pipeline...")
    try:
        clean_production_environment()

        script_data = generate_script(topic)
        engineered_title = engineer_clickbait_title(script_data.get("title", "The Dark Truth"))
        logger.info(f"🎯 Structured Production Title: {engineered_title}")

        voiceover_payload = generate_voiceover(script_data["voiceover"], "temp_voice_stream", voice_type="guy_dark")

        video_clips_paths = download_live_pexels_broll(script_data["scenes"])
        if not video_clips_paths:
            raise RuntimeError("Live Video Scraper Engine returned empty stack.")

        resolved_bgm_path = dynamic_auto_music_downloader(topic)

        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        
        compile_final_video(video_clips_paths, voiceover_payload, resolved_bgm_path, str(output_video_file))

        if output_video_file.exists() and output_video_file.stat().st_size > 0:
            logger.info(f"✨ PIPELINE EXECUTION SUCCESSFUL. Size: {output_video_file.stat().st_size} bytes")
        else:
            raise FileNotFoundError("Render complete but output target payload is missing.")

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
