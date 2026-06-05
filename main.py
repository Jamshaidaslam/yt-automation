"""
main.py — Master Automation Executive Workflow (v5.5 - MULTI-TUNNEL BACKUP)
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
    """Deploys with dual-tunnel automated failover redundancy for Meta Graph API compliance."""
    logger.info("🌐 Mapping binary video block to primary cloud tunnel (file.io)...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.post('https://file.io/?expires=1d', files={'file': f})
            data = response.json()
            if data.get('success'):
                return data.get('link')
    except:
        logger.warning("⚠️ Primary tunnel failed. Initializing secondary backup cluster (tmpfiles.org)...")
        
    try:
        # Secondary backup engine endpoint if file.io is down or ratelimited
        with open(file_path, 'rb') as f:
            res = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f})
            data = res.json()
            if res.status_code == 200 and 'data' in data:
                # Convert standard view URL to direct absolute download stream link
                url = data['data']['url']
                return url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    except Exception as e:
        logger.error(f"❌ All public cloud tunnels exhausted: {e}")
    return None

def execute_pipeline(topic: str):
    logger.info("🔥 Activating Automated High Retention Workflow...")
    try:
        clean_production_environment()
        
        # 1. Script Node
        script_data = generate_script(topic)
        
        # 2. Audio Node
        voiceover_payload = generate_voiceover(script_data["voiceover"], "temp_voice_stream", voice_type="guy_dark")
        
        # 3. Media Download
        video_clips_paths = download_live_pexels_broll(script_data["scenes"])
        resolved_bgm_path = dynamic_auto_music_downloader()

        # 4. Compiler Core Render
        output_video_file = FINAL_OUTPUT_DIR / "final_dark_short_output.mp4"
        compile_final_video(video_clips_paths, voiceover_payload, resolved_bgm_path, str(output_video_file))

        if not (output_video_file.exists() and output_video_file.stat().st_size > 0):
            raise FileNotFoundError("Render payload missing.")
            
        logger.info("✨ VIDEO PIPELINE COMPILED. Triggering Distribution Channels...")

        title = script_data.get("title", "The Dark Truth")
        caption = f"{title}\n\n#darkpsychology #manipulation #mindcontrol #shorts #reels"
        tags = ["dark psychology", "shorts", "reels", "manipulation"]

        # --- YouTube Module ---
        if os.path.exists("token.pickle"):
            logger.info("📡 Dispatching asset stream to YouTube Data API pipeline...")
            try:
                upload_to_youtube(str(output_video_file), title, caption, tags)
            except Exception as yt_err:
                logger.error(f"❌ YouTube upload crashed: {yt_err}")
        else:
            logger.warning("⚠️ token.pickle was not found on the workspace. YouTube deployment skipped.")

        # --- Instagram Module ---
        insta_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        meta_token = os.getenv("META_ACCESS_TOKEN")
        
        if insta_id and meta_token:
            public_video_url = deploy_temporary_public_url(str(output_video_file))
            if public_video_url:
                logger.info("📡 Dispatching asset stream to Meta Graph Cloud Matrix...")
                try:
                    upload_to_instagram(public_video_url, caption, insta_id, meta_token)
                except Exception as meta_err:
                    logger.error(f"❌ Meta Reels upload crashed: {meta_err}")
            else:
                logger.error("❌ Instagram upload skipped: Public file link generation failed.")
        else:
            logger.warning("⚠️ Meta environment credentials missing from secrets setup. Instagram skipped.")

    except Exception as e:
        logger.critical("🚨 MASTER PIPELINE CRASHED!", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="")
    args = parser.parse_args()
    target_topic = args.topic if args.topic.strip() else "How your phone uses dark psychology as a dopamine trap"
    execute_pipeline(target_topic)
