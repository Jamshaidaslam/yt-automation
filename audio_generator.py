"""
audio_generator.py — Edge-TTS Voiceover Pipeline with 403 Auto-Retry
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import asyncio
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

import edge_tts
from tenacity import retry, stop_after_attempt, wait_exponential
from script_generator import build_word_timings
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# ═══════════════════════════════════════════════════════════════════════════════
# CORE TTS FUNCTION WITH RETRY PATCH FOR 403 ERRORS
# ═══════════════════════════════════════════════════════════════════════════════

# FIX: Agar Microsoft 403 block de, to yeh decorator 4 baar automatic retry karega gaps k sath
@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=4, max=15),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(f"TTS blocked (403/Connection issues). Retrying in a few seconds... (Attempt {retry_state.attempt_number})")
)
def _run_synthesis_sync(communicate, out_mp3, out_timings):
    """Helper sync function to aggregate edge-tts async generator with retry stability."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    raw_words = []
    submaker = edge_tts.SubMaker()
    
    async def _gather():
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                with open(out_mp3, "ab") as f:
                    f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
                raw_words.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10000000,
                    "end": (chunk["offset"] + chunk["duration"]) / 10000000
                })
                
    # Fresh clean file setup
    if out_mp3.exists():
        out_mp3.unlink()
        
    loop.run_until_complete(_gather())
    loop.close()
    return raw_words


def generate_voiceover(script: str, output_stem: str) -> dict:
    """
    Main entrypoint for generating high quality audio tracking file outputs.
    """
    audio_path = config.AUDIO_DIR / f"{output_stem}.mp3"
    timings_path = config.AUDIO_DIR / f"{output_stem}_timings.json"

    logger.info(f"Synthesising TTS audio voice using voice: {config.TTS_VOICE}")

    communicate = edge_tts.Communicate(
        text   = script,
        voice  = config.TTS_VOICE,
        rate   = config.TTS_RATE,
        volume = config.TTS_VOLUME,
    )

    try:
        # Retry logic execution
        word_timings = _run_synthesis_sync(communicate, audio_path, timings_path)
    except Exception as e:
        logger.error(f"Edge-TTS fundamentally failed after maximum retries: {e}")
        raise e

    # Fallback structure validation
    duration_sec = _get_audio_duration_sec(audio_path)
    if not word_timings:
        logger.warning("No precise word boundaries extracted. Building fallback linear distributions.")
        word_timings = build_word_timings(script, duration_sec)

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
    test_text = "Testing the robust secure automated edge synthesis runtime framework layer."
    print(generate_voiceover(test_text, "test_stability"))
