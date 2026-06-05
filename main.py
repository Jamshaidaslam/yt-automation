"""
main.py — Production Automation Controller Matrix
AI Dark Realities · Cross-Platform Deployment Engine
───────────────────────────────────────────────────────────────────────────────────
"""
import os
import json
import logging
import requests
from script_generator import generate_script
from video_compiler import compile_final_video
from uploader_youtube import upload_to_youtube
from uploader_instagram import upload_to_instagram

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def deploy_temporary_public_url(file_path):
    """Deploys the video to a temporary public server so Meta Graph API can pull it."""
    logger.info("🌐 Mapping binary video block to public cloud tunnel...")
    try:
        with open(file_path, 'rb') as f:
            # 100% Free 1-day temporary anonymous hosting for Meta processing nodes
            response = requests.post('https://file.io/?expires=1d', files={'file': f})
            data = response.json()
            if data.get('success'):
                return data.get('link')
            else:
                raise RuntimeError(f"Cloud mapping failed: {data}")
    except Exception as e:
        logger.error(f"❌ Critical temporary hosting error: {e}")
        return None

def main():
    logger.info("🚀 Booting Automation Workflow Cluster...")
    
    # 1. Base Variables & Topic Configurations
    topic = "Dark Psychology Manipulation Traps"
    video_output = "final_dark_short_output_5.mp4"
    
    # Fake/Placeholder asset lists - assume your download architecture populates this array
    raw_video_assets = ["assets/clip1.mp4", "assets/clip2.mp4", "assets/clip3.mp4"] 
    bgm_track = "audio/ambient_dark.mp4" 

    # 2. Narrative Engine Trigger
    script_data = generate_script(topic)
    
    # Synthetic schema dictionary required by video compiler layer
    # (Assuming voiceover generation process has populated voiceover_output.mp3 & word_timings beforehand)
    voiceover_payload = {
        "audio_path": "audio/voiceover_output.mp3",
        "word_timings": [
            {"word": "Your", "start": 0.0, "end": 0.4},
            {"word": "phone", "start": 0.4, "end": 0.9},
            {"word": "controls", "start": 0.9, "end": 1.4},
            {"word": "your", "start": 1.4, "end": 1.8},
            {"word": "entire", "start": 1.8, "end": 2.3},
            {"word": "mind", "start": 2.3, "end": 3.0}
        ]
    }
    
    # 3. Dynamic Rendering Sequence
    compile_final_video(
        video_clips_paths=raw_video_assets,
        voiceover_data=voiceover_payload,
        bgm_file_path=bgm_track,
        output_path=video_output
    )
    
    # 4. Cross-Platform Secure API Upload Node
    title = script_data.get("title", "The Dark Truth")
    caption = f"{title}\n\n#darkpsychology #manipulation #mindcontrol #shorts #reels"
    tags = ["dark psychology", "shorts", "reels", "manipulation"]
    
    # --- YouTube Section ---
    if os.path.exists("token.pickle"):
        try:
            upload_to_youtube(video_output, title, caption, tags)
        except Exception as yt_err:
            logger.error(f"❌ YouTube API deployment dropped: {yt_err}")
            
    # --- Instagram Section ---
    insta_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    meta_token = os.getenv("META_ACCESS_TOKEN")
    
    if insta_id and meta_token:
        public_video_url = deploy_temporary_public_url(video_output)
        if public_video_url:
            try:
                upload_to_instagram(public_video_url, caption, insta_id, meta_token)
            except Exception as meta_err:
                logger.error(f"❌ Meta Reels deployment dropped: {meta_err}")
        else:
            logger.error("❌ Instagram upload skipped: Public URL mapping engine returned None.")

if __name__ == "__main__":
    main()
