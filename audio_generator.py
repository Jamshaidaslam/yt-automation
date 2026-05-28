"""
audio_generator.py — Anti-Block Google TTS + FFmpeg Voice Modulator
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
    """
    Generates vocal audio track using Google TTS and modulates it 
    via FFmpeg filters to create a cinematic, non-robotic dark voice.
    """
    raw_audio_path = config.AUDIO_DIR / f"{output_stem}_raw.mp3"
    final_audio_path = config.AUDIO_DIR / f"{output_stem}.mp3"
    timings_path = config.AUDIO_DIR / f"{output_stem}_timings.json"

    logger.info("Synthesising safe voiceover via Google TTS Engine...")

    try:
        # 1. Download raw stable audio stream from Google Translate panel
        tts = gTTS(text=script, lang="en", tld="com", slow=False)
        tts.save(str(raw_audio_path))
        
        # 2. Modulate pitch & speed using local FFmpeg to make it sound like a deep cinematic human
        logger.info("Applying cinematic voice modulation via FFmpeg...")
        if final_audio_path.exists():
            final_audio_path.unlink()

        # Filter adds slight deepness and optimizes resonance
        cmd = [
            "ffmpeg", "-y", "-i", str(raw_audio_path),
            "-af", "asetrate=44100*0.88,atempo=1.14,equalizer=f=250:width_type=o:w=1:g=4",
            str(final_audio_path)
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        # Clean up temporary raw file
        if raw_audio_path.exists():
            raw_audio_path.unlink()
            
        logger.info(f"Cinematic voice track saved -> {final_audio_path.name}")
        
    except Exception as e:
        logger.error(f"Audio production layer failed critically: {e}")
        if raw_audio_path.exists():
            raw_audio_path.unlink()
        raise e

    # Extract precise duration of the modulated audio
    duration_sec = _get_audio_duration_sec(final_audio_path)

    # Distribute caption tracking boundaries
    logger.info("Aligning automated subtitle timing nodes...")
    word_timings = build_word_timings(script, duration_sec)

    # Save tracking json file mapping configuration metrics
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
