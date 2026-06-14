"""
main.py — Automated Production Executive Matrix (v11.0 - FULL STABLE FIX)
AI Dark Realities · Short-Form Video Pipeline
"""

import os
import sys
import logging
import requests
import argparse
import subprocess
from pathlib import Path

from PIL import Image

# PIL compatibility fix
try:
    _ = Image.Resampling
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    Image.ANTIALIAS = Image.LANCZOS

from script_generator import generate_script, pick_topic_for_run
from audio_generator import generate_voiceover
from video_compiler import compile_final_video
from media_fetcher import generate_professional_thumbnail

# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

MEDIA_CACHE_DIR = Path("output/media")
FINAL_OUTPUT_DIR = Path("output/final_videos")


# ─────────────────────────────────────────────
def clean_production_environment():
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
def run_cmd(cmd: str):
    """Safe subprocess wrapper instead of os.system"""
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ─────────────────────────────────────────────
def download_live_pexels_broll(scenes: list) -> list:
    logger.info("🌐 Fetching B-roll from Pexels...")

    api_key = os.getenv("PEXELS_API_KEY")
    downloaded = []
    headers = {"Authorization": api_key} if api_key else {}

    if not scenes:
        scenes = [{"visual_query": "dark psychology cinematic"}]

    for idx, scene in enumerate(scenes):

        query = scene.get("visual_query", "dark psychology eyes")
        clip_path = MEDIA_CACHE_DIR / f"broll_{idx+1}.mp4"

        if clip_path.exists():
            clip_path.unlink()

        success = False

        if api_key:
            try:
                url = "https://api.pexels.com/videos/search"
                params = {
                    "query": query,
                    "per_page": 5,
                    "orientation": "portrait"
                }

                response = requests.get(url, headers=headers, params=params, timeout=15)

                if response.status_code == 200:
                    videos = response.json().get("videos", [])

                    if videos:
                        files = videos[0].get("video_files", [])
                        valid = [f for f in files if f.get("link")]

                        if valid:
                            best = sorted(valid, key=lambda x: abs(x.get("width", 0) - 1080))[0]
                            run_cmd(f'curl -L -o "{clip_path}" "{best["link"]}"')

                            if clip_path.exists() and clip_path.stat().st_size > 15000:
                                downloaded.append(str(clip_path))
                                success = True

            except Exception as e:
                logger.warning(f"Pexels error: {e}")

        if not success:
            logger.warning(f"Fallback clip generated: {query}")
            run_cmd(
                f'ffmpeg -y -f lavfi -i testsrc=duration=6:size=1080x1920:rate=30 '
                f'-c:v libx264 -pix_fmt yuv420p "{clip_path}"'
            )
            downloaded.append(str(clip_path))

    return downloaded


# ─────────────────────────────────────────────
def execute_pipeline(topic: str = "", skip_upload: bool = False):

    logger.info("🔥 Starting Automated Video Pipeline...")

    try:
        clean_production_environment()

        if not topic:
            topic = pick_topic_for_run()
            logger.info(f"🔄 Auto-selected topic: {topic}")

        # 1. SCRIPT
        script_data = generate_script(topic) or {}

        voice_text = script_data.get("voiceover", topic)

        # FIX: ONLY supported voices
        voiceover_path = generate_voiceover(
            text=voice_text,
            output_name="voice.mp3",
            voice_type="female"
        )

        # 2. BROLL
        video_clips = download_live_pexels_broll(script_data.get("scenes", []))

        # 3. THUMBNAIL
        scenes = script_data.get("scenes", [])
        keyword_query = scenes[0].get("visual_query", topic) if scenes else topic

        thumb_path = generate_professional_thumbnail(
            keyword=keyword_query,
            line1=script_data.get("thumbnail_line1", "WATCH NOW"),
            line2=script_data.get("thumbnail_line2", "SEE THE TRUTH"),
            output_stem="frame_trap"
        )

        # intro injection
        if thumb_path:
            intro_clip = MEDIA_CACHE_DIR / "intro.mp4"
            run_cmd(
                f'ffmpeg -y -loop 1 -i "{thumb_path}" -t 0.5 '
                f'-vf "scale=1080:1920" -c:v libx264 -pix_fmt yuv420p "{intro_clip}"'
            )
            video_clips.insert(0, str(intro_clip))

        # 4. COMPILE
        output_video = FINAL_OUTPUT_DIR / "final_output.mp4"

        compile_final_video(
            video_clips_paths=video_clips,
            voiceover_data=voiceover_path,   # FIXED: string only
            bgm_file_path="output/media/bgm.mp3" if os.path.exists("output/media/bgm.mp3") else "",
            output_path=str(output_video)
        )

        # 5. VERIFY
        if output_video.exists() and output_video.stat().st_size > 50000:
            logger.info(f"✨ SUCCESS: {output_video}")

            if skip_upload:
                return

            seo = {
                "title": script_data.get("title", topic),
                "description": script_data.get("description", ""),
                "hashtags": script_data.get("tags", "")
            }

            if os.path.exists("uploader.py"):
                try:
                    import uploader
                    uploader.upload_all_platforms(
                        video_path=str(output_video),
                        seo=seo,
                        thumbnail_path=thumb_path
                    )
                except Exception as e:
                    logger.error(f"Upload failed: {e}")

        else:
            raise Exception("Video compilation failed")

    except Exception:
        logger.critical("🚨 PIPELINE CRASHED!", exc_info=True)
        sys.exit(1)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    parser.add_argument("--skip-upload", action="store_true")
    args = parser.parse_args()

    execute_pipeline(topic=args.topic.strip(), skip_upload=args.skip_upload)
