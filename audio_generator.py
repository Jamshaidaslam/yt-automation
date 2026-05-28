"""
audio_generator.py — Clean Standard TTS Engine
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import json
import logging
import subprocess
from pathlib import Path
from gtts import gTTS
from script_generator import build_word_timings
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

def generate_voiceover(script: str, output_stem: str) -> dict:
    final_audio_path = config.AUDIO_DIR / f"{output_stem}.mp3"
    timings_path = config.AUDIO_DIR / f"{output_stem}_timings.json"

    logger.info("Synthesising clean voiceover via Google TTS Engine...")

    try:
        if final_audio_path.exists():
            final_audio_path.unlink()

        # Generate clean standard audio without breaking speed/pitch
        tts = gTTS(text=script, lang="en", tld="com", slow=False)
        tts.save(str(final_audio_path))
        logger.info(f"Voice track saved successfully -> {final_audio_path.name}")
        
    except Exception as e:
        logger.error(f"Audio production layer failed critically: {e}")
        raise e

    duration_sec = _get_audio_duration_sec(final_audio_path)
    logger.info("Aligning automated subtitle timing nodes...")
    word_timings = build_word_timings(script, duration_sec)

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
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())
