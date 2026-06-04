"""
main.py — Master Automation Executive Workflow (PRODUCTION ENGINE v2.8 - LIVE DOWNLOADER)
AI Dark Realities · Short-Form Video Pipeline
Fixed: Replaced local asset fallbacks with live automated Pexels API media downloader.
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import shutil
import logging
import requests
from pathlib import Path
from script_generator import generate_script
from audio_generator import generate_voiceover
from video_compiler import compile_final_video

# Setup production logger rules
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Master Absolute Path Definitions
MEDIA_CACHE_DIR = Path("output/media")
FINAL_OUTPUT_DIR = Path("output/final_videos")
BGM_INPUT_DIR = Path("assets/bgm")

def clean_production_environment():
    """Wipes old cached video items completely to prevent duplicate visual leaks."""
    logger.info("🧹 Performing complete media cache clean reset...")
    if MEDIA_CACHE_DIR.exists():
        shutil.rmtree(MEDIA_CACHE_DIR)
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BGM_INPUT_DIR.mkdir(parents=True, exist_ok=True)

def download_live_pexels_broll(scenes: list) -> list:
    """Fetches high-aesthetic cinematic vertical stock video links via live Pexels API."""
    logger.info("🌐 Activating live Pexels API media scraper engine...")
    api_key = os.getenv("PEXELS_API_KEY")
    
    if not api_key:
        logger.warning("⚠️ PEXELS_API_KEY missing! Falling back to empty stack array.")
        return []

    downloaded_paths = []
    headers = {"Authorization": api_key}

    for idx, scene in enumerate(scenes):
        query = scene.get("visual_query", "dark psychology")
        logger.info(f"🔍 Searching Pexels stock stream for Clip [{idx+1}]: '{query}'")
        
        url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page=5&orientation=portrait"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                videos = data.get("videos", [])
                if videos:
                    # Select premium mobile resolution stream safely
                    video_files = videos[0].get("video_files", [])
                    # Filter for clean vertical HD streams
                    hd_files = [f for f in video_files if f.get("quality") == "hd" or f.get("width", 0) >= 720]
                    target_file = hd_files[0] if hd_files else (video_files[0] if video_files else None)
                    
                    if target_file:
                        download_url = target_file["link"]
                        clip_path = MEDIA_CACHE_DIR / f"broll_scene_{idx+1}.mp4"
                        
                        logger.info(f"📥 Downloading active visual payload: {download_url}")
                        v_resp = requests.get(download_url, stream=True, timeout=30)
                        with open(clip_path, "wb") as f:
                            for chunk in v_resp.iter_content(chunk_size=1024*1024):
                                if chunk: f.write(chunk)
                                
                        downloaded_paths.append(str(clip_path))
                        continue
            logger.warning(f"⚠️ Pexels stream empty for '{query}', trying fallback dynamic prompt...")
        except Exception as e:
            logger.error(f"❌ Scraper failure on scene block [{idx+1}]: {e}")

    return downloaded_paths

def create_emergency_fallback_bgm():
    """Generates an asset folder and ensures a background score file exists."""
    # Agar assets/bgm khali ho to crash na ho, system ensure karega background track ko
    test_bgm = BGM_INPUT_DIR / "ambient_suspense.mp3"
    if not any(BGM_INPUT_DIR.glob("*.mp3")):
        logger.warning(f"⚠️ Background music directory empty. Please drop a cinematic score track in {BGM_INPUT_DIR}")
        # Placeholder indicator to prevent initial boot failure if assets aren't pushed yet
        raise FileNotFoundError(f"Please drop at least one cinematic background music .mp3 track inside the '{BGM_INPUT_DIR}' directory.")

def engineer_clickbait_title(raw_title: str) -> str:
    """Forces AI raw titles into elite automated psychology loop hooks."""
    clean_title = raw_title.replace('"', '').strip()
    if not clean_title.endswith("..."):
        clean_title += "..."
    return f"🧠 {clean_title} #darkpsychology #manipulation #shorts"

def execute_pipeline(topic: str):
    """Orchestrates the entire automated audio-visual framework from script to file output."""
    logger.info("🔥 Activating Automated Dark Realities Script Sequence Pipeline...")
    
    # Step 1: Wipe workspace cache completely
    clean_production_environment()

    # Step 2: Generate elite script context from LLM
    script_data = generate_script(topic)
    engineered_title = engineer_clickbait_title(script_data.get("title", "The Dark Truth"))
    logger.info(f"🎯 Structured Production Title: {engineered_title}")

    # Step 3: Synthesis voiceover audio tracking with automatic radar evasion pitch shifts
    voiceover_payload = generate_voiceover(script_data["voiceover"], "temp_voice_stream", voice_type="guy_dark")

    # Step 4: Download Fresh Live B-Roll Clips via Pexels API Scraper
    video_clips_paths = download_live_pexels_broll(script_data["scenes"])
    
    if not video_clips_paths:
        raise RuntimeError("Live Video Scraper Engine returned an empty array block. Verify PEXELS_API_KEY tokens.")

    # Step 5: Ensure Background Music file is active
    create_emergency_fallback_bgm()

    # Step 6: Compile Final Composition Output
    output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
    compile_final_video(video_clips_paths, voiceover_payload, str(BGM_INPUT_DIR), str(output_video_file))

    logger.info(f"✨ PIPELINE EXECUTION SUCCESSFUL. Ready for distribution: {output_video_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args = parser.parse_args()
    
    # Safe fallback parameter allocation
    target_topic = args.topic if args.topic.strip() else "How your phone uses dark psychology as a dopamine trap"
    execute_pipeline(target_topic)
