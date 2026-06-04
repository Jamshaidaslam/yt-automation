"""
main.py — Master Neural Influence Pipeline (PRO-VIRAL v8.1)
Update: Increased clip density for 50s+ duration.
"""

import os, logging, random, sys, shutil
from pathlib import Path
from script_generator import generate_script
from audio_generator import generate_voiceover
from media_fetcher import fetch_broll_clips
from video_compiler import compile_final_video

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

MEDIA_CACHE_DIR = Path("output/media")
FINAL_OUTPUT_DIR = Path("output/final_videos")

def clean_and_prep():
    if MEDIA_CACHE_DIR.exists(): shutil.rmtree(MEDIA_CACHE_DIR)
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def execute_pipeline(topic: str):
    logger.info(f"🚀 Initializing Viral Pipeline for: {topic}")
    try:
        clean_and_prep()

        # 1. Script
        script_data = generate_script(topic)
        
        # 2. Voice (Aapka trained RVC Model yahan call ho raha hai)
        voice_data = generate_voiceover(script_data["voiceover"], "main_voice")

        # 3. Fetching Visuals (Limit 10 clips per keyword = 20-30 clips total)
        # 20+ clips * 2.5s = 50 seconds video.
        visual_queries = script_data.get("visual_queries", ["dark atmosphere", "minimalist psychology", "high status lifestyle"])
        video_paths = fetch_broll_clips(visual_queries, clips_per_keyword=10) 

        # 4. Cinematic Render
        output_path = FINAL_OUTPUT_DIR / "final_viral_production.mp4"
        compile_final_video(video_paths, voice_data, "assets/music/dark.mp3", str(output_path))
        
        logger.info(f"✅ Pipeline complete: {output_path}")
        return output_path

    except Exception as e:
        logger.critical(f"🚨 Pipeline Crash: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Ab 50 second ki video ke liye topic pool ready hai
    pool = [
        "How to use the Half-Sentence Trap to make her obsess over you",
        "The silent sub-cue that makes people instantly submit to your status",
        "How to read a woman's true intentions in under 3 seconds",
        "The psychological pause that forces authority in any room",
        "Why being 'too available' kills your attraction and how to fix it"
    ]
    
    topic = random.choice(pool)
    execute_pipeline(topic)
