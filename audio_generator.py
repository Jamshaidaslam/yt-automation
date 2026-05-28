"""
audio_generator.py — Edge-TTS Premium Voice Engine
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
import edge_tts
from script_generator import build_word_timings
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def generate_voiceover(script: str, output_stem: str) -> dict:
    """
    Generates vocal audio track using Edge-TTS premium neural engines.
    """
    audio_path = config.AUDIO_DIR / f"{output_stem}.mp3"
    timings_path = config.AUDIO_DIR / f"{output_stem}_timings.json"

    logger.info(f"Synthesising premium voice narration via Edge-TTS [{config.TTS_VOICE}]...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

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
                with open(audio_path, "ab") as f:
                    f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
                raw_words.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10000000,
                    "end": (chunk["offset"] + chunk["duration"]) / 10000000
                })

    if audio_path.exists():
        audio_path.unlink()

    try:
        loop.run_until_complete(_gather())
    finally:
        loop.close()

    duration_sec = _get_audio_duration_sec(audio_path)

    if not raw_words:
        logger.warning("Precise boundaries missing, generating fallbacks...")
        word_timings = build_word_timings(script, duration_sec)
    else:
        word_timings = raw_words

    timings_path.write_text(json.dumps(word_timings, indent=2), encoding="utf-8")

    return {
        "audio_path":   str(audio_path),
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
