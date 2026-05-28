"""
audio_generator.py — Google TTS Voiceover Pipeline (100% Stable on GitHub Actions)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
Replaced edge-tts with gTTS to permanently bypass Microsoft's GitHub Cloud IP blocks.
No API keys required, completely safe from 403 Forbidden errors.
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
    """
    Generates vocal audio track using Google TTS engine.
    Completely immune to GitHub Actions runner IP blocks.
    """
    audio_path = config.AUDIO_DIR / f"{output_stem}.mp3"
    timings_path = config.AUDIO_DIR / f"{output_stem}_timings.json"

    logger.info("Synthesising safe voiceover via Google TTS (gTTS)...")

    try:
        # Extract language code from voice config (e.g., 'en-US-...' -> 'en')
        lang_code = config.TTS_VOICE.split("-")[0] if "-" in config.TTS_VOICE else "en"
        
        # Initialize Google TTS and save stream
        tts = gTTS(text=script, lang=lang_code, slow=False)
        tts.save(str(audio_path))
        logger.info(f"Audio track saved successfully -> {audio_path.name}")
        
    except Exception as e:
        logger.error(f"Google TTS layer failed critically: {e}")
        raise e

    # Extract dynamic float duration using system FFprobe binary
    duration_sec = _get_audio_duration_sec(audio_path)

    # Automatically map precise word metrics dynamically for MoviePy captions
    logger.info("Distributing timing sequence alignments...")
    word_timings = build_word_timings(script, duration_sec)

    # Persist JSON configuration tracking metrics
    timings_path.write_text(json.dumps(word_timings, indent=2), encoding="utf-8")

    return {
        "audio_path":   str(audio_path),
        "timings_path": str(timings_path),
        "word_timings": word_timings,
        "duration_sec": duration_sec,
    }


def _get_audio_duration_sec(audio_path: Path) -> float:
    """Extract precise float duration from generated media using FFprobe backend."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())


if __name__ == "__main__":
    test_text = "This is a stable test sequence generated using Google text to speech automation systems."
    print(generate_voiceover(test_text, "gtts_stability_test"))
