"""
main.py — Master Neural Influence Pipeline (PRO-VIRAL v8.0)
Architecture:
  1. Viral Loop Sequencing: Forces infinite video retention.
  2. Multi-Timezone Dispatch: Schedules for USA/UK peak hours.
  3. Visual Metaphor Mapping: Maps scripts to high-authority visual queries.
"""

import os, logging, random, sys, shutil
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

def clean_and_prep():
    """Reset environment for new viral cycle."""
    if MEDIA_CACHE_DIR.exists(): shutil.rmtree(MEDIA_CACHE_DIR)
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def engineer_metadata(script_data):
    """Engineers high-CTR clickbait with perfect loop hooks."""
    raw_title = script_data.get("title", "The Unspoken Code")
    # Ensuring the title is a cliffhanger
    hook = f"{raw_title.replace('...', '')}..." 
    tags = ["#DarkPsychology", "#MindControl", "#Status", "#ReadPeople", "#Viral"]
    return f"🧠 {hook} {' '.join(tags)}"

def execute_pipeline(topic: str):
    logger.info(f"🚀 Initializing Viral Pipeline for: {topic}")
    try:
        clean_and_prep()

        # 1. Script with Infinite Loop Hook
        script_data = generate_script(topic)
        
        # 2. Voice (Deep British Authority)
        voice_data = generate_voiceover(script_data["voiceover"], "main_voice")

        # 3. Fetching Visual Metaphors (Targeting 1M+ View Aesthetics)
        visual_queries = script_data.get("visual_queries", ["dark atmosphere", "minimalist psychology"])
        video_paths = fetch_broll_clips(visual_queries, clips_per_keyword=2)

        # 4. Cinematic Render (Vignette + Zoom)
        output_path = FINAL_OUTPUT_DIR / "final_viral_production.mp4"
        compile_final_video(video_paths, voice_data, "assets/music/dark.mp3", str(output_path))

        # 5. Metadata & Deployment
        seo = {
            "title": engineer_metadata(script_data),
            "description": f"{script_data['voiceover'][:150]}... Follow for daily neural codes.",
            "hashtags": ["#DarkPsychology", "#Manipulation", "#Status", "#Shorts"]
        }
        
        logger.info(f"✅ Pipeline complete: {output_path}")
        return output_path

    except Exception as e:
        logger.critical(f"🚨 Pipeline Crash: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args = parser.parse_args()

    # Fallback pool for USA/UK Viral content
    pool = [
        "How to use the Half-Sentence Trap to make her obsess over you",
        "The silent sub-cue that makes people instantly submit to your status",
        "How to read a woman's true intentions in under 3 seconds",
        "The psychological pause that forces authority in any room",
        "Why being 'too available' kills your attraction and how to fix it"
    ]
    
    topic = args.topic if args.topic else random.choice(pool)
    execute_pipeline(topic)
