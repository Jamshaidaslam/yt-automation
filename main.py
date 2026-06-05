"""
main.py — Master Automation Executive Workflow (PRODUCTION ENGINE v5.0 - PATH MATRIX SYNC)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
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

from script_generator import generate_script
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
    logger.info("🧹 Performing complete media cache clean reset...")
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BGM_INPUT_DIR.mkdir(parents=True, exist_ok=True)

def download_live_pexels_broll(scenes: list) -> list:
    logger.info("🌐 Activating live Pexels API 12-node split engine...")
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
                            download_url = target_file["link"]
                            os.system(f'curl -L -s -o "{clip_path}" "{download_url}"')
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
    if local_bgms: return str(local_bgms[0])
    target_track_path = BGM_INPUT_DIR / "dynamic_scraped_bgm.mp3"
    static_url = "https://assets.mixkit.co/music/preview/mixkit-glitchy-futuristic-ambient-mystery-1149.mp3"
    try:
        os.system(f'curl -L -s -o "{target_track_path}" "{static_url}"')
        if target_track_path.exists(): return str(target_track_path)
    except: pass
    return ""

def deploy_temporary_public_url(file_path):
    logger.info("🌐 Mapping binary video block to public cloud tunnel...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.post('https://file.io/?expires=1d', files={'file': f})
            data = response.json()
            if data.get('success'):
                return data.get('link')
            else:
                raise RuntimeError(f"Cloud mapping failed: {data}")
    except Exception as e:
        logger.error(f"❌ Critical temporary hosting error: {e}")
        return None

def execute_pipeline(topic: str):
    logger.info("🔥 Activating Automated High Retention Workflow...")
    try:
        clean_production_environment()
        
        # 1. Script Generation
        script_data = generate_script(topic)
        
        # 2. Audio Generation (SSML Pitch Shifts + SubMaker Sync)
        # Dynamic variable mapping saves directly to output/media/temp_voice_stream.mp3
        voiceover_payload = generate_voiceover(script_data["voiceover"], "temp_voice_stream", voice_type="guy_dark")
        
        # 3. Download Media B-Roll Assets
        video_clips_paths = download_live_pexels_broll(script_data["scenes"])
        resolved_bgm_path = dynamic_auto_music_downloader()

        # 4. Rendering Step
        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        compile_final_video(video_clips_paths, voiceover_payload, resolved_bgm_path, str(output_video_file))

        if not (output_video_file.exists() and output_video_file.stat().st_size > 0):
            raise FileNotFoundError("Render payload missing.")
            
        logger.info("✨ VIDEO PIPELINE COMPILED. Triggering Distribution Node...")

        title = script_data.get("title", "The Dark Truth")
        caption = f"{title}\n\n#darkpsychology #manipulation #mindcontrol #shorts #reels"
        tags = ["dark psychology", "shorts", "reels", "manipulation"]

        # --- YouTube Upload ---
        try:
            upload_to_youtube(str(output_video_file), title, caption, tags)
        except Exception as yt_err:
            logger.error(f"❌ YouTube upload skipped: {yt_err}")

        # --- Instagram Upload ---
        insta_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        meta_token = os.getenv("META_ACCESS_TOKEN")
        
        if insta_id and meta_token:
            public_video_url = deploy_temporary_public_url(str(output_video_file))
            if public_video_url:
                try:
                    upload_to_instagram(public_video_url, caption, insta_id, meta_token)
                except Exception as meta_err:
                    logger.error(f"❌ Meta Reels upload skipped: {meta_err}")
            else:
                logger.error("❌ Instagram upload aborted: Cloud URL tunnel returned None.")

    except Exception as e:
        logger.critical("🚨 PIPELINE CRASHED!", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args = parser.parse_args()
    target_topic = args.topic if args.topic.strip() else "How your phone uses dark psychology as a dopamine trap"
    execute_pipeline(target_topic)
