"""
audio_generator.py — Edge-TTS Voiceover Pipeline (Fixed Object Stream Crash)
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
# CORE TTS PIPELINE WITH FIX FOR ATTEMPT REUSE
# ═══════════════════════════════════════════════════════════════════════════════

# FIX: Tenacity retry loop ab naye fresh object k sath execute hoga har bar
@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=4, max=15),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"TTS stream blocked or network glitch. Creating fresh stream session... (Attempt {retry_state.attempt_number})"
    )
)
def _execute_synthesis_with_retry(script: str, out_mp3: Path):
    """
    Creates a FRESH Communicate instance on every single retry attempt 
    to completely prevent 'RuntimeError: stream can only be called once'.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Generate fresh clean instance mapping configurations
    communicate = edge_tts.Communicate(
        text   = script,
        voice  = config.TTS_VOICE,
        rate   = config.TTS_RATE,
        volume = config.TTS_VOLUME,
    )
    
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
                
    # Reset/clean old file if it was partially written in a failed attempt
    if out_mp3.exists():
        out_mp3.unlink()
        
    try:
        loop.run_until_complete(_gather())
        return raw_words
    finally:
        loop.close()


def generate_voiceover(script: str, output_stem: str) -> dict:
    """
    Main entrypoint for generating high quality audio tracking file outputs.
    """
    audio_path = config.AUDIO_DIR / f"{output_stem}.mp3"
    timings_path = config.AUDIO_DIR / f"{output_stem}_timings.json"

    logger.info(f"Synthesising TTS audio voice using voice: {config.TTS_VOICE}")

    try:
        # Run safe fresh object instantiation pipeline execution
        word_timings = _execute_synthesis_with_retry(script, audio_path)
    except Exception as e:
        logger.error(f"Edge-TTS structurally blocked after maximum attempts: {e}")
        raise e

    # Calculate final duration metrics
    duration_sec = _get_audio_duration_sec(audio_path)
    
    if not word_timings:
        logger.warning("No precise word boundaries extracted. Building fallback linear distributions.")
        word_timings = build_word_timings(script, duration_sec)

    # Save outputs tracking json file array
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
    test_text = "Testing the stream runtime instance creation pipeline layer wrapper framework."
    print(generate_voiceover(test_text, "test_stream_safety"))
