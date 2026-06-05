"""
audio_generator.py — Production Voice Synthesis Layer (v5.1 - ZERO-FAIL SYNC LOCK)
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
BASE_RATE  = "+0%"
BASE_PITCH = "-4Hz"

# ─── Podcast Style Filter ──────────────────────────────────────────────────────
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
            logger.warning(f"⚠️ ffmpeg filter failed — using raw audio")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning(f"⚠️ ffmpeg not available: {e} — using raw audio")
        return False


async def _extract_boundaries_fallback(plain_text: str) -> list:
    """Dedicated secondary pass to extract word boundaries if the primary stream misses them."""
    word_timings = []
    communicate = edge_tts.Communicate(plain_text, VOICE_ID, rate=BASE_RATE, pitch=BASE_PITCH)
    accumulated_pause = 0.0
    
    async for chunk in communicate.stream():
        if chunk["type"] == "WordBoundary":
            start_sec = (chunk["offset"] / 10_000_000.0) + accumulated_pause
            duration_sec = chunk["duration"] / 10_000_000.0
            word_clean = chunk["text"]
            
            break_duration = 0.0
            if word_clean.endswith(".") or word_clean.endswith("!") or word_clean.endswith("?"):
                break_duration = 0.55
            elif word_clean.endswith(","):
                break_duration = 0.30
                
            word_timings.append({
                "word": word_clean.upper(),
                "start": round(start_sec, 3),
                "end": round(start_sec + duration_sec, 3)
            })
            accumulated_pause += break_duration
            
    return word_timings


def generate_voiceover(text_script: str, output_filename: str, voice_type: str = "guy_dark") -> dict:
    logger.info(f"🎙️ Activating Zero-Fail Sync Stream Matrix...")

    output_dir = Path("output/media")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_audio_path    = output_dir / f"{output_filename}_raw.mp3"
    target_audio_path = output_dir / f"{output_filename}.mp3"

    for p in [raw_audio_path, target_audio_path]:
        if p.exists():
            try: p.unlink()
            except: pass

    # Clean text input from potential formatting and emoji glitches
    clean_text_stream = re.sub(r'[^\w\s\.,!\?\']', '', text_script)
    clean_text_stream = " ".join(clean_text_stream.strip().split())

    word_timings = []
    
    # Pass 1: Render High-Quality Voice Track Natively
    try:
        communicate = edge_tts.Communicate(clean_text_stream, VOICE_ID, rate=BASE_RATE, pitch=BASE_PITCH)
        
        async def run_audio_save():
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    with open(raw_audio_path, "ab") as f:
                        f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary" and len(word_timings) < 5:
                    # Collect early boundaries if available
                    pass

        asyncio.run(run_audio_save())
        logger.info("✅ Audio asset stream rendered successfully.")
    except Exception as stream_err:
        logger.error(f"❌ Pass 1 Audio Render crash: {stream_err}")

    # Pass 2: Forced Core Boundary Extraction Guarantee
    try:
        logger.info("🔍 Syncing boundary timestamps matrix...")
        word_timings = asyncio.run(_extract_boundaries_fallback(clean_text_stream))
        logger.info(f"✅ Boundaries extraction complete. Synced words count: {len(word_timings)}")
    except Exception as boundary_err:
        logger.critical(f"❌ Pass 2 boundary extractor failed: {boundary_err}")
        word_timings = []

    # ── Master Podcast Filter Execution Node ─────────────────────────────────
    filter_success = apply_podcast_filter(raw_audio_path, target_audio_path)
    if not filter_success:
        import shutil
        shutil.copy(str(raw_audio_path), str(target_audio_path))
        logger.warning("⚠️ Bypassed audio master track. Reverted to raw stream.")

    if raw_audio_path.exists():
        try: raw_audio_path.unlink()
        except: pass

    # Resolve video timeline metrics
    try:
        from moviepy.editor import AudioFileClip
        real_duration = AudioFileClip(str(target_audio_path)).duration
    except:
        real_duration = word_timings[-1]["end"] if word_timings else 30.0

    # Safety Fallback: Enforce math-based timing chunks if API returns absolutely empty blocks
    if not word_timings:
        logger.warning("⚠️ Boundary array empty! Enforcing calculated math fallback presets...")
        current_time = 0.0
        for word in clean_text_stream.split():
            dur = 0.35 if len(word) > 5 else 0.25
            word_timings.append({
                "word": word.upper(),
                "start": round(current_time, 3),
                "end": round(current_time + dur, 3)
            })
            current_time += dur + 0.05

    # ── Safe CTA Overlap Filter ──────────────────────────────────────────────
    # Hides normal subtitles 3.5 seconds before video ends to let the persistent CTA stand out cleanly
    safe_cutoff_mark = max(0.0, real_duration - 3.5)
    word_timings = [word for word in word_timings if word["start"] < safe_cutoff_mark]
    logger.info(f"🛡️ CTA Protection Layer applied. Active display captions: {len(word_timings)}")

    return {
        "audio_path":   str(target_audio_path),
        "word_timings": word_timings,
        "duration":     real_duration
                }
