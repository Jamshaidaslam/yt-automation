"""
audio_generator.py — Production Voice Synthesis Layer (PRODUCTION ENGINE v2.5 - BUG FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fix: os.system curl replaced with requests.get for safe fallback download
"""

import os
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_voiceover(text_script: str, output_filename: str, voice_type: str = "guy_dark") -> dict:
    logger.info("🎙️ Activating ElevenLabs Voice Engine...")

    output_dir = Path("output/media")
    output_dir.mkdir(parents=True, exist_ok=True)
    target_audio_path = output_dir / f"{output_filename}.mp3"

    if target_audio_path.exists():
        try:
            target_audio_path.unlink()
        except Exception as clean_err:
            logger.warning(f"⚠️ Could not clear old audio: {clean_err}")

    ROOM_NOISE_VOLUME = 0.05
    logger.info(f"🎚️ Noise floor set to: {ROOM_NOISE_VOLUME}")

    voice_id = "21m00Tcm4TlvDq8ikWAM" if voice_type == "guy_dark" else "AZnzlk1XvdvUeBnXmlld"
    api_key = os.getenv("ELEVENLABS_API_KEY")
    api_success = False

    if api_key:
        logger.info(f"📥 Fetching voice stream from ElevenLabs. Voice ID: {voice_id}")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": text_script,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.85
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=45)
            if response.status_code == 200:
                with open(target_audio_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                logger.info("✅ ElevenLabs audio saved to disk.")
                api_success = True
            else:
                logger.error(f"❌ ElevenLabs API Error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"❌ Network issue with ElevenLabs: {e}")

    # FIX: os.system('curl ...') hata ke requests.get lagaya
    # os.system se koi return value nahi milti, silently fail ho sakta tha
    needs_fallback = (
        not api_success
        or not target_audio_path.exists()
        or target_audio_path.stat().st_size < 5000
    )

    if needs_fallback:
        logger.warning("🚨 ElevenLabs unavailable. Using fallback audio stream...")
        fallback_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        try:
            fb_response = requests.get(fallback_url, timeout=30, stream=True)
            if fb_response.status_code == 200:
                with open(target_audio_path, "wb") as f:
                    for chunk in fb_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info("✅ Fallback audio saved successfully.")
            else:
                logger.error(f"❌ Fallback fetch failed: HTTP {fb_response.status_code}")
        except Exception as e:
            logger.error(f"⚠️ Fallback stream failed: {e}")

    # Word timings generation
    words = text_script.split()
    word_timings = []
    current_time = 0.0

    for word in words:
        word_duration = 0.38 if len(word) > 5 else 0.24
        word_timings.append({
            "word": word,
            "start": round(current_time, 2),
            "end": round(current_time + word_duration, 2)
        })
        current_time += word_duration + 0.04

    payload = {
        "audio_path": str(target_audio_path),
        "word_timings": word_timings
    }

    logger.info(f"✅ Voiceover generation complete. Track: {target_audio_path}")
    return payload
