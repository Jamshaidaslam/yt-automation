"""
audio_generator.py — Edge-TTS Voiceover Pipeline
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
Uses the edge-tts library (free Microsoft Azure neural TTS) to:
  1. Synthesise the narration script into a high-quality MP3 voiceover.
  2. Capture per-word boundary events to produce precise caption timings.
  3. Save both the audio file and a JSON sidecar with word timings.

Falls back to evenly distributed timings if word boundaries are unavailable.
"""

import asyncio
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

import edge_tts
from script_generator import build_word_timings
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# ═══════════════════════════════════════════════════════════════════════════════
# CORE TTS FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

async def _synthesise(script: str, out_mp3: Path, out_timings: Path) -> list[dict]:
    """
    Async synthesis via edge-tts.
    Returns list of {word, start, end} dicts (seconds, float).
    """
    communicate = edge_tts.Communicate(
        text   = script,
        voice  = config.TTS_VOICE,
        rate   = config.TTS_RATE,
        volume = config.TTS_VOLUME,
    )

    raw_words: list[dict] = []   # Collected from word-boundary events

    # ── Stream audio + word boundary events ─────────────────────────────────
    with open(out_mp3, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # edge-tts provides offset in 100-nanosecond ticks
                offset_ticks   = chunk.get("offset", 0)
                duration_ticks = chunk.get("duration", 0)
                start_sec = offset_ticks   / 1e7
                end_sec   = (offset_ticks + duration_ticks) / 1e7
                word      = chunk.get("text", "").strip()
                if word:
                    raw_words.append({
                        "word":  re.sub(r"[^\w''-]", "", word),  # strip punctuation
                        "start": round(start_sec, 3),
                        "end":   round(end_sec,   3),
                    })

    logger.info(f"TTS synthesis complete → {out_mp3.name}  |  {len(raw_words)} word events")

    # ── Persist timings sidecar ──────────────────────────────────────────────
    out_timings.write_text(json.dumps(raw_words, indent=2), encoding="utf-8")
    return raw_words


def _get_audio_duration_sec(mp3_path: Path) -> float:
    """Use ffprobe to read the exact duration of the rendered MP3."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of",           "default=noprint_wrappers=1:nokey=1",
                str(mp3_path),
            ],
            capture_output=True, text=True, check=True,
        )
        return float(result.stdout.strip())
    except Exception as exc:
        logger.warning(f"ffprobe duration check failed: {exc} — estimating from word count.")
        return 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def generate_voiceover(script: str, output_stem: str) -> dict:
    """
    Synthesise a voiceover for `script` and return metadata dict:
    {
        "audio_path":   str   — path to .mp3 file,
        "timings_path": str   — path to JSON sidecar,
        "word_timings": list  — [{word, start, end}, ...],
        "duration_sec": float — total audio length in seconds,
    }

    Parameters
    ----------
    script      : str  — narration text from Groq
    output_stem : str  — base filename (no extension), e.g. "video_20240601_001"
    """
    out_mp3      = config.AUDIO_DIR / f"{output_stem}.mp3"
    out_timings  = config.AUDIO_DIR / f"{output_stem}_timings.json"

    # ── Run async synthesis inside a new event loop (safe for any context) ──
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    try:
        word_timings = loop.run_until_complete(
            _synthesise(script, out_mp3, out_timings)
        )
    finally:
        loop.close()

    # ── Get exact audio duration ─────────────────────────────────────────────
    duration_sec = _get_audio_duration_sec(out_mp3)
    if duration_sec <= 0:
        # Estimate: average English speaking rate ~150 wpm at our slower setting
        word_count   = len(script.split())
        duration_sec = word_count / 2.2   # ~132 wpm equivalent

    # ── Fallback: distribute timings evenly if edge-tts gave no events ──────
    if not word_timings:
        logger.warning("No word-boundary events received. Using fallback even distribution.")
        word_timings = build_word_timings(script, duration_sec)
        # Persist fallback timings
        out_timings.write_text(json.dumps(word_timings, indent=2), encoding="utf-8")

    logger.info(
        f"Voiceover ready: duration={duration_sec:.2f}s | "
        f"words={len(word_timings)} | file={out_mp3.name}"
    )

    return {
        "audio_path":   str(out_mp3),
        "timings_path": str(out_timings),
        "word_timings": word_timings,
        "duration_sec": duration_sec,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# OPTIONAL: LOAD LOCAL CLONED VOICE  (alternative to edge-tts)
# ═══════════════════════════════════════════════════════════════════════════════

def use_local_voice(audio_path: str, script: str) -> dict:
    """
    Use a pre-rendered local audio file (e.g. from a voice cloning tool)
    instead of edge-tts.  Timings are derived evenly from the audio duration.

    Parameters
    ----------
    audio_path : str  — path to an existing .mp3 / .wav file
    script     : str  — narration text (used for timing distribution)
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Local voice file not found: {audio_path}")

    duration_sec = _get_audio_duration_sec(audio_path)
    word_timings = build_word_timings(script, duration_sec)

    timings_path = audio_path.with_suffix("_timings.json")
    timings_path.write_text(json.dumps(word_timings, indent=2), encoding="utf-8")

    return {
        "audio_path":   str(audio_path),
        "timings_path": str(timings_path),
        "word_timings": word_timings,
        "duration_sec": duration_sec,
    }


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    TEST_SCRIPT = (
        "Right now, a camera somewhere is scanning your face without your knowledge. "
        "AI surveillance systems process over one billion images every single day, "
        "mapping the movements of ordinary people in real time. Governments and private "
        "corporations purchase this data legally. Your face is a product. "
        "The scariest part? In most countries there is no law stopping this. "
        "Follow for more dark realities that the tech industry doesn't want you to know."
    )
    result = generate_voiceover(TEST_SCRIPT, "test_audio")
    print(f"Duration: {result['duration_sec']:.2f}s")
    print(f"Words timed: {len(result['word_timings'])}")
    print(f"Audio: {result['audio_path']}")
