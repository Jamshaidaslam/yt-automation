"""
main.py — Automated Production Executive Matrix (v10.8 - WORKFLOW PARAMETER LOCK)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import logging
import requests
import argparse
from pathlib import Path

# FIX: PIL Attribute Error (ANTIALIAS issue for rendering layers)
from PIL import Image
try:
    getattr(Image, 'Resampling')
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    Image.ANTIALIAS = Image.LANCZOS

from script_generator import generate_script, pick_topic_for_run
from audio_generator import generate_voiceover
from video_compiler import compile_final_video

# Setup System Level Logging Stream
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

MEDIA_CACHE_DIR = Path("output/media")
FINAL_OUTPUT_DIR = Path("output/final_videos")


def clean_production_environment():
    """Wipes old runtime state and initializes environment safely."""
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_live_pexels_broll(scenes: list) -> list:
    """Fetches cinematic portrait assets from Pexels API dynamically."""
    logger.info("🌐 Fetching B-roll from Pexels...")
    api_key = os.getenv("PEXELS_API_KEY")
    downloaded_paths = []
    headers = {"Authorization": api_key} if api_key else {}

    for idx, scene in enumerate(scenes):
        query = scene.get("visual_query", "dark psychology eyes microexpression")
        clip_path = MEDIA_CACHE_DIR / f"broll_scene_{idx+1}.mp4"
        
        if clip_path.exists():
            try: clip_path.unlink()
            except: pass

        success = False
        if api_key:
            url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page=5&orientation=portrait"
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    videos = response.json().get("videos", [])
                    if videos:
                        video_files = videos[0].get("video_files", [])
                        valid_files = [f for f in video_files if f.get("link") and f.get("file_type") == "video/mp4"]
                        
                        if valid_files:
                            target_file = sorted(valid_files, key=lambda x: abs(x.get("width", 0) - 1080))[0]
                            video_link = target_file["link"]
                            
                            logger.info(f"📥 Downloading asset file node: {query}")
                            os.system(f'curl -L -s -o "{clip_path}" "{video_link}"')
                            
                            if clip_path.exists() and clip_path.stat().st_size > 15000:
                                downloaded_paths.append(str(clip_path))
                                logger.info(f"✅ Clip {idx+1} downloaded successfully")
                                success = True
            except Exception as e:
                logger.warning(f"⚠️ Pexels fetch error: {e}")

        if not success:
            logger.warning(f"🔄 Reverted to dynamic fallback generation for: {query}")
            os.system(f'ffmpeg -y -f lavfi -i testsrc=duration=6:size=1080x1920:rate=30 -c:v libx264 -pix_fmt yuv420p "{clip_path}" > /dev/null 2>&1')
            downloaded_paths.append(str(clip_path))

    return downloaded_paths


def execute_pipeline(topic: str = "", skip_upload: bool = False):
    """Core executive control structure linking atomic automation components."""
    logger.info("🔥 Starting Automated Video Pipeline...")
    try:
        if not topic:
            topic = pick_topic_for_run()
            logger.info(f"🔄 Auto-selected topic from viral pool: {topic}")
        
        clean_production_environment()

        # 1. AI Script Generation Matrix
        script_data = generate_script(topic)

        # 2. Audio Voiceover Rendering with Dynamic Rescale
        voiceover_payload = generate_voiceover(
            script_data["voiceover"],
            "temp_voice_stream",
            voice_type="guy_dark"
        )

        # 3. Dynamic B-Roll Fetch Engine
        video_clips_paths = download_live_pexels_broll(script_data.get("scenes", []))
        
        # 4. Hollywood Style Short-Form Video Compositor
        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        resolved_bgm_track = "output/media/bgm.mp3" if os.path.exists("output/media/bgm.mp3") else ""

        compile_final_video(
            video_clips_paths=video_clips_paths, 
            voiceover_data=voiceover_payload, 
            bgm_file_path=resolved_bgm_track, 
            output_path=str(output_video_file)
        )

        # ── Verification Check ────────────────────────────────────────────────
        if output_video_file.exists() and output_video_file.stat().st_size > 50000:
            logger.info(f"✨ Pipeline finished successfully! Video saved at: {output_video_file}")
            
            # 5. AUTOMATIC SOCIAL MEDIA UPLOAD TRIGGER 🚀
            if skip_upload:
                logger.info("ℹ️ Skip upload parameter detected via workflow engine — Posting Aborted.")
                return

            logger.info("🛰️ Initializing Automatic Social Media Upload Matrix...")
            
            real_title = script_data.get("title", topic if topic else "Dark Psychology Secrets")
            real_description = script_data.get("voiceover", "Watch till the end to uncover the truth.")
            
            seo_payload = {
                "title": real_title,
                "description": real_description,
                "hashtags": ["#darkpsychology", "#manipulation", "#psychologyfacts", "#shorts", "#Shorts", "#microexpression"]
            }
            
            if os.path.exists("uploader.py"):
                try:
                    logger.info("📦 Importing central uploader engine and pushing streams...")
                    import uploader
                    
                    # Call exact upload function from uploader.py
                    upload_logs = uploader.upload_all_platforms(
                        video_path=str(output_video_file),
                        seo=seo_payload,
                        thumbnail_path=None
                    )
                    logger.info(f"📊 Central uploader completed execution. Results array: {upload_logs}")
                except Exception as up_err:
                    logger.error(f"❌ Central uploader module runtime crash: {up_err}")
            else:
                logger.warning("⚠️ uploader.py was not found in root workspace directory.")
                
        else:
            raise Exception("Compilation failed - output short-form file was not compiled correctly.")

    except Exception:
        logger.critical("🚨 PIPELINE EXECUTOR MATRIX CRASHED!", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    # FIXED: Added support for the --skip-upload flag dispatched by automate.yml
    parser.add_argument("--skip-upload", action="store_true", help="Skip social media upload step.")
    args = parser.parse_args()
    
    execute_pipeline(topic=args.topic.strip(), skip_upload=args.skip_upload)
