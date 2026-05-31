"""
audio_generator.py — High-Retention Unique Voice Engine (Edge-TTS Custom Frequency)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import asyncio
import json
import logging
import subprocess
import re
from pathlib import Path
import edge_tts
from script_generator import build_word_timings
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

def clean_script_text(raw_text: str) -> str:
    """
    Script mein se har tarah ke website links, URLs, ads aur faltu symbols
    ko saaf karne ka function taake robot ghalat cheezain na parhe.
    """
    # 1. Agar text mein koi web address (http/https/www) ya .com jaisa kuch hai to saaf karo
    clean_text = re.sub(r'https?://\S+|www\.\S+', '', raw_text)
    clean_text = re.sub(r'\S+\.(com|net|org|edu|gov|pk|info)\S*', '', clean_text)
    
    # 2. Markdown symbols aur extra spaces saaf karein
    clean_text = re.sub(r'[#\*\_\]\[\(\)]', '', clean_text)
    clean_text = " ".join(clean_text.split())
    
    return clean_text

def generate_voiceover(script: str, output_stem: str) -> dict:
    final_audio_path = config.AUDIO_DIR / f"{output_stem}.mp3"
    timings_path = config.AUDIO_DIR / f"{output_stem}_timings.json"

    logger.info("Synthesizing 100% Unique frequency voiceover via Edge Cloud...")

    # Pehle script ko har tarah ke links se bilkul pak-saaf karein
    clean_script = clean_script_text(script)
    
    if not clean_script:
        logger.error("Script text bilkul khali ho gaya cleaning ke baad! Using fallback text.")
        clean_script = "Beware of the shadows, for they reveal the darkest realities."

    try:
        if final_audio_path.exists():
            final_audio_path.unlink()

        # Christopher ke bajaye British Accent 'Ryan' use kar rahe hain jo aam nahi hai
        voice_character = "en-GB-RyanNeural"
        
        # Pitch -12Hz (Bhari aur mysterious) aur Rate +5% (Grip banaye rakhne ke liye)
        custom_pitch = "-12Hz"
        custom_rate = "+5%"

        async def save_voice():
            communicate = edge_tts.Communicate(
                clean_script,
                voice_character,
                rate=custom_rate,
                pitch=custom_pitch
            )
            await communicate.save(str(final_audio_path))

        asyncio.run(save_voice())
        logger.info(f"Unique Deep Male Voice track saved successfully -> {final_audio_path.name}")

    except Exception as e:
        logger.error(f"Audio production failed critically: {e}")
        raise e

    duration_sec = _get_audio_duration_sec(final_audio_path)

    logger.info("Aligning automated subtitle timing nodes...")
    # Timings hamesha clean script par hi banni chahiye taake subtitle sync rahein
    word_timings = build_word_timings(clean_script, duration_sec)

    timings_path.write_text(json.dumps(word_timings, indent=2), encoding="utf-8")

    return {
        "audio_path":   str(final_audio_path),
        "timings_path": str(timings_path),
        "word_timings": word_timings,
        "duration_sec": duration_sec,
    }


def _get_audio_duration_sec(audio_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ]
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return float(res.stdout.strip())
