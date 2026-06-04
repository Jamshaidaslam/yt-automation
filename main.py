"""
main.py — Master Automation Executive Workflow (PRODUCTION ENGINE v3.2 - DIAGNOSTIC WRAPPER)
AI Dark Realities · Short-Form Video Pipeline
Upgraded: Added explicit exception catching and path verification to catch moviepy silent exits.
───────────────────────────────────────────────────────────────────────────────────
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
from video_compiler import compile_final_video

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

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
                        v_resp = requests.get(download_url, stream=True, timeout=30)
                        with open(clip_path, "wb") as f:
                            for chunk in v_resp.iter_content(chunk_size=1024*1024):
                                if chunk: f.write(chunk)
                        downloaded_paths.append(str(clip_path))
                        logger.info(f"✅ Downloaded clip saved to: {clip_path}")
        except Exception as e:
            logger.error(f"❌ Scraper failure on scene [{idx+1}]: {e}")
    return downloaded_paths

def dynamic_auto_music_downloader(topic: str) -> str:
    """Ensures a background score track exists, or auto-downloads matching the theme."""
    local_bgms = list(BGM_INPUT_DIR.glob("*.mp3")) + list(BGM_INPUT_DIR.glob("*.wav"))
    if local_bgms:
        logger.info("🎵 Using existing local background music file asset.")
        return str(local_bgms[0])

    target_track_path = BGM_INPUT_DIR / "dynamic_scraped_bgm.mp3"
    search_keywords = "dark suspense ambient thriller" if ("dark" in topic.lower() or "psychology" in topic.lower()) else "suspense cinematic ambient"
    
    pixabay_key = os.getenv("PIXABAY_API_KEY")
    if pixabay_key:
        logger.info(f"🔍 Searching Pixabay Audio Repository for keywords: '{search_keywords}'")
        url = f"https://pixabay.com/api/videos/audio/?key={pixabay_key}&q={requests.utils.quote(search_keywords)}&per_page=10"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                hits = response.json().get("hits", [])
                if hits:
                    download_url = random.choice(hits).get("audio", "")
                    if download_url:
                        logger.info("📥 Stream-downloading uncorrupted Pixabay audio...")
                        audio_resp = requests.get(download_url, stream=True, allow_redirects=True, timeout=45)
                        with open(target_track_path, "wb") as f:
                            for chunk in audio_resp.iter_content(chunk_size=32 * 1024):
                                if chunk: f.write(chunk)
                        if target_track_path.stat().st_size > 5000:
                            return str(target_track_path)
        except Exception as e:
            logger.error(f"❌ Pixabay API track failure: {e}")

    logger.warning("🚨 Downloading secure backup mystery theme asset...")
    static_url = "https://assets.mixkit.co/music/preview/mixkit-glitchy-futuristic-ambient-mystery-1149.mp3"
    response = requests.get(static_url, stream=True, allow_redirects=True, timeout=30)
    with open(target_track_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=32 * 1024):
            if chunk: f.write(chunk)
    return str(target_track_path)

def engineer_clickbait_title(raw_title: str) -> str:
    """Forces AI raw titles into elite automated psychology loop hooks."""
    clean_title = raw_title.replace('"', '').strip()
    if not clean_title.endswith("..."):
        clean_title += "..."
    return f"🧠 {clean_title} #darkpsychology #manipulation #shorts"

def execute_pipeline(topic: str):
    """Orchestrates the entire automated audio-visual framework with raw safety catchers."""
    logger.info("🔥 Activating Automated Dark Realities Script Sequence Pipeline...")
    
    try:
        clean_production_environment()

        # Step 1: Script Context Generation
        script_data = generate_script(topic)
        engineered_title = engineer_clickbait_title(script_data.get("title", "The Dark Truth"))
        logger.info(f"🎯 Structured Production Title: {engineered_title}")

        # Step 2: Audio Synthesis & Pitch Evasion
        voiceover_payload = generate_voiceover(script_data["voiceover"], "temp_voice_stream", voice_type="guy_dark")
        logger.info(f"🎙️ Voiceover generated payload checked: {voiceover_payload}")

        # Step 3: Video Downloader Scraper
        video_clips_paths = download_live_pexels_broll(script_data["scenes"])
        if not video_clips_paths:
            raise RuntimeError("Live Video Scraper Engine returned an empty array block. No clips downloaded.")
        logger.info(f"🎬 Downloaded video clips stack count: {len(video_clips_paths)}")

        # Step 4: Topic-Aware Dynamic Audio Scraper
        resolved_bgm_path = dynamic_auto_music_downloader(topic)
        logger.info(f"🎵 Background music track successfully resolved at: {resolved_bgm_path}")

        # Step 5: Render Final Video Composition
        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        logger.info(f"🎬 Sending parameters to MoviePy Compiler engine. Output path target: {output_video_file}")
        
        compile_final_video(video_clips_paths, voiceover_payload, resolved_bgm_path, str(output_video_file))

        # Final Post-verification check
        if output_video_file.exists() and output_video_file.stat().st_size > 0:
            logger.info(f"✨ PIPELINE EXECUTION SUCCESSFUL. File generated: {output_video_file} (Size: {output_video_file.stat().st_size} bytes)")
        else:
            raise FileNotFoundError(f"MoviePy rendering step finished but the output file does not exist at {output_video_file}!")

    except Exception as pipeline_error:
        # 🔥 CRITICAL LOG PRINT: Explicitly captures internal compilation failures so they print out in GitHub Actions
        logger.critical("🚨 PIPELINE CRASHED INSIDE CORE EXECUTION BLOCK!", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args = parser.parse_args()
    
    target_topic = args.topic if args.topic.strip() else "How your phone uses dark psychology as a dopamine trap"
    execute_pipeline(target_topic)
