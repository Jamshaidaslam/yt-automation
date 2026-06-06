"""
audio_generator.py — Production Voice Synthesis Layer (v5.2 - STREAMING SYNC REPAIR)
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
            logger.warning("⚠️ ffmpeg filter failed — using raw audio")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning(f"⚠️ ffmpeg not available: {e} — using raw audio")
        return False


def generate_voiceover(text_script: str, output_filename: str, voice_type: str = "guy_dark") -> dict:
    logger.info("🎙️ Activating Zero-Fail Sync Stream Matrix...")

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

    async def run_combined_stream():
        communicate = edge_tts.Communicate(clean_text_stream, VOICE_ID, rate=BASE_RATE, pitch=BASE_PITCH)
        # Single-pass parsing: Audio aur Timestamps aik sath fetch honge
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                with open(raw_audio_path, "ab") as f:
                    f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Naye Edge-TTS mapping objects ko standard coordinate dictionaries me convert karein
                start_sec = chunk.get("offset", 0) / 10_000_000.0
                duration_sec = chunk.get("duration", 0) / 10_000_000.0
                text_word = chunk.get("text", "")
                
                if text_word:
                    word_timings.append({
                        "word": text_word.upper(),
                        "start": round(start_sec, 3),
                        "end": round(start_sec + duration_sec, 3)
                    })

    try:
        asyncio.run(run_combined_stream())
        logger.info(f"✅ Audio rendered & Boundaries synced. Words count: {len(word_timings)}")
    except Exception as stream_err:
        logger.error(f"❌ Audio/Boundary Stream Engine Crash: {stream_err}")

    # Master Podcast Filter Execution Node
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

    # Smart Mathematical Fallback Engine (Agar API bilkul hi zero response de)
    if not word_timings:
        logger.warning("⚠️ Boundary array empty! Enforcing calculated math fallback presets...")
        current_time = 0.0
        for word in clean_text_stream.split():
            dur = 0.38 if len(word) > 5 else 0.28
            word_timings.append({
                "word": word.upper(),
                "start": round(current_time, 3),
                "end": round(current_time + dur, 3)
            })
            current_time += dur + 0.04

    # ── Master Safe CTA Overlap Filter ───────────────────────────────────────
    # Normal captions ko end se 3.2 seconds pehle freeze karein taaki persistent CTA overlay clear dikhe
    safe_cutoff_mark = max(0.0, real_duration - 3.2)
    word_timings = [word for word in word_timings if word["start"] < safe_cutoff_mark]
    logger.info(f"🛡️ CTA Protection Layer applied. Active display captions: {len(word_timings)}")

    return {
        "audio_path":   str(target_audio_path),
        "word_timings": word_timings,
        "duration":     real_duration
            }
