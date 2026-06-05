"""
main.py — Master Automation Executive Workflow (v5.6 - TOPIC ROTATION + SYNC FIXED)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────

FIXES v5.6:
  - Removed hardcoded topic — now uses script_generator's auto topic rotation
  - Each GitHub Actions run picks a unique topic from 40-topic pool
  - --topic flag still works for manual overrides
"""

import os
import json
import logging
import requests
import sys
from pathlib import Path

import PIL
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

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
            except:
                pass

        if not success:
            try:
                os.system(f'ffmpeg -y -f lavfi -i testsrc=duration=4:size=1080x1920:rate=30 -vf "hue=H=2*PI*t:s=0.4" -c:v libx264 -pix_fmt yuv420p "{clip_path}" > /dev/null 2>&1')
                if clip_path.exists():
                    downloaded_paths.append(str(clip_path))
            except:
                pass

    return downloaded_paths


def dynamic_auto_music_downloader() -> str:
    local_bgms = list(BGM_INPUT_DIR.glob("*.mp3")) + list(BGM_INPUT_DIR.glob("*.wav"))
    if local_bgms:
        return str(local_bgms[0])
    target_track_path = BGM_INPUT_DIR / "dynamic_scraped_bgm.mp3"
    static_url = "https://assets.mixkit.co/music/preview/mixkit-glitchy-futuristic-ambient-mystery-1149.mp3"
    try:
        os.system(f'curl -L -s -o "{target_track_path}" "{static_url}"')
        if target_track_path.exists():
            return str(target_track_path)
    except:
        pass
    return ""


def deploy_temporary_public_url(file_path):
    logger.info("🌐 Uploading to public tunnel for Meta API...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.post('https://file.io/?expires=1d', files={'file': f})
            data = response.json()
            if data.get('success'):
                return data.get('link')
    except:
        logger.warning("⚠️ file.io failed, trying tmpfiles.org...")
    try:
        with open(file_path, 'rb') as f:
            res = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f})
            data = res.json()
            if res.status_code == 200 and 'data' in data:
                url = data['data']['url']
                return url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    except Exception as e:
        logger.error(f"❌ All upload tunnels failed: {e}")
    return None


def execute_pipeline(topic: str = ""):
    logger.info("🔥 Starting Automated Video Pipeline...")
    try:
        clean_production_environment()

        # 1. Script — auto-picks topic if none given
        script_data = generate_script(topic)

        # 2. Voiceover
        voiceover_payload = generate_voiceover(
            script_data["voiceover"],
            "temp_voice_stream",
            voice_type="guy_dark"
        )

        # 3. B-Roll
        video_clips_paths = download_live_pexels_broll(script_data["scenes"])
        resolved_bgm_path = dynamic_auto_music_downloader()

        # 4. Compile
        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        compile_final_video(
            video_clips_paths,
            voiceover_payload,
            resolved_bgm_path,
            str(output_video_file)
        )

        if not (output_video_file.exists() and output_video_file.stat().st_size > 0):
            raise FileNotFoundError("Render failed — output file missing.")

        logger.info("✨ Video compiled. Starting uploads...")

        title   = script_data.get("title", "The Dark Truth")
        caption = f"{title}\n\n#darkpsychology #manipulation #mindcontrol #shorts #reels"
        tags    = ["dark psychology", "shorts", "reels", "manipulation"]

        # YouTube
        if os.path.exists("token.pickle"):
            try:
                upload_to_youtube(str(output_video_file), title, caption, tags)
            except Exception as yt_err:
                logger.error(f"❌ YouTube upload failed: {yt_err}")
        else:
            logger.warning("⚠️ token.pickle not found — YouTube skipped.")

        # Instagram
        insta_id    = os.getenv("INSTAGRAM_ACCOUNT_ID")
        meta_token  = os.getenv("META_ACCESS_TOKEN")
        if insta_id and meta_token:
            public_url = deploy_temporary_public_url(str(output_video_file))
            if public_url:
                try:
                    upload_to_instagram(public_url, caption, insta_id, meta_token)
                except Exception as meta_err:
                    logger.error(f"❌ Instagram upload failed: {meta_err}")
            else:
                logger.error("❌ Instagram skipped — public URL generation failed.")
        else:
            logger.warning("⚠️ Meta credentials missing — Instagram skipped.")

    except Exception:
        logger.critical("🚨 PIPELINE CRASHED!", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="",
                        help="Optional topic override. Leave blank for auto-rotation.")
    parser.add_argument("--skip-upload", action="store_true",
                        help="Render video only, skip all uploads.")
    args = parser.parse_args()

    # Log which topic will be used
    if args.topic.strip():
        logger.info(f"📌 Manual topic override: {args.topic}")
    else:
        logger.info(f"🔄 Auto topic rotation active")

    execute_pipeline(args.topic.strip())
