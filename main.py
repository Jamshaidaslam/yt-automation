"""
main.py — Master Automation Executive Workflow (PRODUCTION ENGINE v3.0 - DYNAMIC MUSIC DOWNLOADER)
AI Dark Realities · Short-Form Video Pipeline
Upgraded: Automated dynamic background music scraper matching the exact psychological video topic.
─────────────────────────────────────────────────────────────────────────────────────────────────────
"""

import os
import shutil
import logging
import requests
import random
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
                    video_files = videos[0].get("video_files", [])
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

def dynamic_auto_music_downloader(topic: str):
    """
    🌟 DYNAMIC TOPIC-BASED MUSIC SCRAPER
    If local BGM is missing, connects directly to Pixabay Audio API to scrape 
    premium cinematic/suspense tracks matching the video's theme.
    """
    existing_bgm = list(BGM_INPUT_DIR.glob("*.mp3")) + list(BGM_INPUT_DIR.glob("*.wav"))
    if existing_bgm:
        logger.info("🎵 Local background music assets detected. Skipping dynamic download.")
        return

    logger.warning("⚠️ BGM folder empty! Initializing Automated Topic-Based Music Scraper...")
    
    # Generate intelligent audio search keywords based on your topic context
    search_keywords = "suspense cinematic ambient"
    if "dark" in topic.lower() or "psychology" in topic.lower():
        search_keywords = "dark suspense ambient thriller"
    elif "love" in topic.lower() or "poetry" in topic.lower():
        search_keywords = "sad cinematic piano flute"

    pixabay_key = os.getenv("PIXABAY_API_KEY")
    fallback_track_path = BGM_INPUT_DIR / "dynamic_scraped_bgm.mp3"

    if pixabay_key:
        logger.info(f"🔍 Searching Pixabay Audio Repository for keywords: '{search_keywords}'")
        url = f"https://pixabay.com/api/videos/audio/?key={pixabay_key}&q={requests.utils.quote(search_keywords)}&per_page=10"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                hits = response.json().get("hits", [])
                if hits:
                    random_track = random.choice(hits)
                    download_url = random_track.get("audio", "")
                    if download_url:
                        logger.info(f"📥 Downloading matched Pixabay audio track: {random_track.get('title', 'Cinematic Sound')}")
                        audio_resp = requests.get(download_url, timeout=30)
                        with open(fallback_track_path, "wb") as f:
                            f.write(audio_resp.content)
                        logger.info("✅ Pixabay dynamic background track deployed successfully!")
                        return
        except Exception as e:
            logger.error(f"❌ Pixabay Audio API connection failed: {e}")

    # Ultimate Hardcoded Backup Node if both local folders and Pixabay API limit leaks out
    logger.warning("🚨 Pixabay Audio fallback triggered. Downloading standard dark-mystery asset...")
    static_backup_url = "https://assets.mixkit.co/music/preview/mixkit-glitchy-futuristic-ambient-mystery-1149.mp3"
    try:
        response = requests.get(static_backup_url, timeout=20)
        with open(fallback_track_path, "wb") as f:
            f.write(response.content)
        logger.info("✅ Hardcoded backup cinematic mystery theme loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Ultimate BGM layer crash prevention failed: {e}")
        raise FileNotFoundError(f"Please drop at least one background music .mp3 track inside '{BGM_INPUT_DIR}' folder.")

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

    # Step 5: Dynamic Audio Scraping Layer (Matches video topic perfectly if directory is empty)
    dynamic_auto_music_downloader(topic)

    # Step 6: Compile Final Composition Output
    output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
    compile_final_video(video_clips_paths, voiceover_payload, str(BGM_INPUT_DIR), str(output_video_file))

    logger.info(f"✨ PIPELINE EXECUTION SUCCESSFUL. Ready for distribution: {output_video_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args = parser.parse_args()
    
    target_topic = args.topic if args.topic.strip() else "How your phone uses dark psychology as a dopamine trap"
    execute_pipeline(target_topic)
