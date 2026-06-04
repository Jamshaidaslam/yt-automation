"""
main.py — Master Automation Executive Workflow (PIPELINE ENGINE v2.7)
AI Dark Realities · Short-Form Video Pipeline
Upgraded: Automated absolute Title engineering and strict media caching resets.
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import shutil
import logging
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

    # Step 4: Downloader Placeholder Linkage 
    # (Fake mock download links matching your local Pexels/Pixabay video array integration)
    mock_downloaded_clips = []
    raw_video_source_dir = Path("assets/raw_clips") # Your fallback storage path
    
    if raw_video_source_dir.exists():
        mock_downloaded_clips = [str(p) for p in raw_video_source_dir.glob("*.mp4")][:len(script_data["scenes"])]
        
    if not mock_downloaded_clips:
        raise FileNotFoundError("Please ensure assets/raw_clips folder contains your collection of high-aesthetic dark MP4 assets.")

    # Step 5: Compile Final Composition Output
    output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
    compile_final_video(mock_downloaded_clips, voiceover_payload, str(BGM_INPUT_DIR), str(output_video_file))

    logger.info(f"✨ PIPELINE EXECUTION SUCCESSFUL. Ready for distribution: {output_video_file}")

if __name__ == "__main__":
    # Feel free to change this default topic value anytime during manual workflow dispatches
    execute_pipeline("How your brain fills silence with psychological nightmares")
