"""
audio_generator.py — Production Voice Synthesis Layer (v5.0 - REALTIME SYNC LOCK)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import re
import subprocess
import logging
import asyncio
from pathlib import Path
import edge_tts

logger = logging.getLogger(__name__)

# ─── Voice Config ──────────────────────────────────────────────────────────────
VOICE_ID   = "en-US-EricNeural"
BASE_RATE  = "+4%"
BASE_PITCH = "-2Hz"

# ─── Podcast Style Filter (Filter 2) ──────────────────────────────────────────
PODCAST_FILTER = (
    "highpass=f=80,"
    "lowpass=f=8000,"
    "equalizer=f=1000:width_type=o:width=2:g=2,"
    "equalizer=f=5000:width_type=o:width=2:g=-3,"
    "acompressor=threshold=-20dB:ratio=3:attack=5:release=50"
)


def apply_podcast_filter(input_path: Path, output_path: Path) -> bool:
    """Applies professional podcast mastering filter chain via ffmpeg."""
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(input_path),
                "-af", PODCAST_FILTER,
                "-acodec", "libmp3lame",
                "-q:a", "2",
                str(output_path)
            ],
            capture_output=True,
            timeout=60
        )
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
            logger.info("✅ Podcast filter applied successfully")
            return True
        else:
            logger.warning(f"⚠️ ffmpeg filter failed (code {result.returncode}) — using raw audio")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning(f"⚠️ ffmpeg not available: {e} — using raw audio")
        return False


async def _render_and_extract_timings(plain_text: str, raw_audio_path: Path) -> list:
    """
    Unified Single-Pass Stream Core: Fetches high quality audio binary data 
    and handles conversational millisecond alignment concurrently.
    """
    word_timings = []
    # edge_tts.Communicate does not take is_ssml in standard versions, we use safe string parameters
    communicate = edge_tts.Communicate(plain_text, VOICE_ID, rate=BASE_RATE, pitch=BASE_PITCH)
    
    # Track natural timing shifts based on text dynamics
    accumulated_pause = 0.0

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            with open(raw_audio_path, "ab") as f:
                f.write(chunk["data"])
        
        elif chunk["type"] == "WordBoundary":
            # Convert offset ticks directly to structural seconds
            start_sec = (chunk["offset"] / 10_000_000.0) + accumulated_pause
            duration_sec = chunk["duration"] / 10_000_000.0
            word_clean = chunk["text"]
            
            # Smart Custom SSML Break Emulation via Text Analytics
            break_duration = 0.0
            if word_clean.endswith(".") or word_clean.endswith("!") or word_clean.endswith("?"):
                break_duration = 0.40
            elif word_clean.endswith(","):
                break_duration = 0.20
            
            word_timings.append({
                "word": word_clean.upper(),
                "start": round(start_sec, 3),
                "end": round(start_sec + duration_sec, 3)
            })
            
            # Shift timeline buffer for the next incoming word stream
            accumulated_pause += break_duration

    return word_timings


def generate_voiceover(text_script: str, output_filename: str, voice_type: str = "guy_dark") -> dict:
    logger.info(f"🎙️ Activating Realtime Sync Unified Stream Matrix...")

    output_dir = Path("output/media")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_audio_path    = output_dir / f"{output_filename}_raw.mp3"
    target_audio_path = output_dir / f"{output_filename}.mp3"

    # Wipe stale session components
    for p in [raw_audio_path, target_audio_path]:
        if p.exists():
            try: p.unlink()
            except: pass

    # Clean text payload string from formatting bugs
    clean_text_stream = " ".join(text_script.strip().split())

    # Execute Single-Pass Execution Core
    try:
        word_timings = asyncio.run(_render_and_extract_timings(clean_text_stream, raw_audio_path))
        logger.info(f"✅ Realtime Audio Render Complete. Synced words: {len(word_timings)}")
    except Exception as stream_err:
        logger.critical(f"❌ Core TTS stream layer crashed: {stream_err}")
        word_timings = []

    # ── Master Podcast Filter Execution Node ─────────────────────────────────
    filter_success = apply_podcast_filter(raw_audio_path, target_audio_path)
    if not filter_success:
        import shutil
        shutil.copy(str(raw_audio_path), str(target_audio_path))
        logger.warning("⚠️ Bypassed audio master track. Reverted to unfiltered audio stream.")

    # Drop intermediate files safely
    if raw_audio_path.exists():
        try: raw_audio_path.unlink()
        except: pass

    # Get absolute final duration values
    try:
        from moviepy.editor import AudioFileClip
        real_duration = AudioFileClip(str(target_audio_path)).duration
    except:
        real_duration = word_timings[-1]["end"] if word_timings else 30.0

    # ── Safe CTA Overlap Filter ──────────────────────────────────────────────
    # Trims out subtitle captions for the last 3.5 seconds so they don't clash with the permanent CTA block
    safe_cutoff_mark = max(0.0, real_duration - 3.5)
    word_timings = [word for word in word_timings if word["start"] < safe_cutoff_mark]
    logger.info(f"🛡️ CTA Protection Layer applied. Safe captions pool size: {len(word_timings)}")

    logger.info(f"🎙️ Done | Absolute Duration: {real_duration:.2f}s | Active Word Elements: {len(word_timings)}")

    return {
        "audio_path":   str(target_audio_path),
        "word_timings": word_timings,
        "duration":     real_duration
      }
