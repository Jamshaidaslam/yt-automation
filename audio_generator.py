"""
audio_generator.py — Production Voice Synthesis Layer (v4.1 - PODCAST FILTER)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────

FIXES v4.1:
  - Podcast Style filter added (Filter 2) — applied after TTS render via ffmpeg:
      highpass=80Hz    → removes low rumble, sounds professional
      lowpass=8000Hz   → removes harsh highs, reduces ear fatigue
      equalizer 1kHz +2dB → voice presence and clarity
      equalizer 5kHz -3dB → removes TTS harshness/sibilance
      acompressor       → consistent volume, no loud/soft jumps
  - Word timing capture unchanged (still plain text — sync stays accurate)
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
# Professional podcast mastering chain — same used by top USA/UK creators
# highpass=80        → Cut low rumble & mic noise
# lowpass=8000       → Cut harsh TTS high frequencies
# equalizer 1kHz +2  → Boost voice presence & clarity
# equalizer 5kHz -3  → Reduce TTS sibilance (ssss sounds)
# acompressor        → Even out loud/soft — listener doesn't get fatigued
PODCAST_FILTER = (
    "highpass=f=80,"
    "lowpass=f=8000,"
    "equalizer=f=1000:width_type=o:width=2:g=2,"
    "equalizer=f=5000:width_type=o:width=2:g=-3,"
    "acompressor=threshold=-20dB:ratio=3:attack=5:release=50"
)


def build_audio_ssml(text_script: str) -> str:
    """Builds SSML for audio rendering with natural pauses."""
    script = text_script.replace(", ",  ', <break time="200ms"/> ')
    script = script.replace(". ",  '. <break time="400ms"/> ')
    script = script.replace("! ",  '! <break time="350ms"/> ')
    script = script.replace("? ",  '? <break time="350ms"/> ')

    return f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="{VOICE_ID}">
            <prosody rate="{BASE_RATE}" pitch="{BASE_PITCH}">
                {script}
            </prosody>
        </voice>
    </speak>"""


def apply_podcast_filter(input_path: Path, output_path: Path) -> bool:
    """
    Applies podcast mastering filter chain via ffmpeg.
    Returns True if successful, False if ffmpeg not available.
    """
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(input_path),
                "-af", PODCAST_FILTER,
                "-acodec", "libmp3lame",
                "-q:a", "2",          # High quality MP3
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


async def _render_audio_only(ssml_content: str, output_path: Path):
    """Pass 1: Render raw TTS audio using SSML."""
    communicate = edge_tts.Communicate(ssml_content, VOICE_ID, is_ssml=True)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            with open(output_path, "ab") as f:
                f.write(chunk["data"])


async def _capture_word_timings(plain_text: str) -> list:
    """
    Pass 2: Capture word timings using plain text (no SSML).
    Plain text gives accurate WordBoundary events — SSML break tags
    shift audio timeline but boundary ticks don't follow, causing sync drift.
    """
    word_timings = []
    communicate = edge_tts.Communicate(plain_text, VOICE_ID, rate=BASE_RATE, pitch=BASE_PITCH)
    async for chunk in communicate.stream():
        if chunk["type"] == "WordBoundary":
            start_sec    = chunk["offset"]   / 10_000_000.0
            duration_sec = chunk["duration"] / 10_000_000.0
            word_timings.append({
                "word":  chunk["text"],
                "start": round(start_sec, 3),
                "end":   round(start_sec + duration_sec, 3)
            })
    return word_timings


def generate_voiceover(text_script: str, output_filename: str, voice_type: str = "guy_dark") -> dict:
    logger.info(f"🎙️ Generating voiceover | Voice: {VOICE_ID} | Filter: Podcast Style")

    output_dir = Path("output/media")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_audio_path    = output_dir / f"{output_filename}_raw.mp3"
    target_audio_path = output_dir / f"{output_filename}.mp3"

    # Clean old files
    for p in [raw_audio_path, target_audio_path]:
        if p.exists():
            try: p.unlink()
            except: pass

    # ── Pass 1: Render TTS audio with SSML ───────────────────────────────────
    ssml_content = build_audio_ssml(text_script)
    try:
        asyncio.run(_render_audio_only(ssml_content, raw_audio_path))
        logger.info("✅ TTS render complete")
    except Exception as e:
        logger.error(f"❌ SSML render failed: {e} — falling back to plain")
        communicate = edge_tts.Communicate(text_script, VOICE_ID, rate=BASE_RATE, pitch=BASE_PITCH)
        asyncio.run(communicate.save(str(raw_audio_path)))

    # ── Apply Podcast Filter via ffmpeg ───────────────────────────────────────
    filter_success = apply_podcast_filter(raw_audio_path, target_audio_path)

    if not filter_success:
        # If filter failed, use raw audio directly
        import shutil
        shutil.copy(str(raw_audio_path), str(target_audio_path))
        logger.warning("⚠️ Using unfiltered audio")

    # Clean up raw temp file
    try:
        raw_audio_path.unlink()
    except:
        pass

    # ── Pass 2: Capture word timings (plain text — accurate sync) ─────────────
    word_timings = []
    try:
        word_timings = asyncio.run(_capture_word_timings(text_script))
        logger.info(f"✅ Word timings synced: {len(word_timings)} words")
    except Exception as e:
        logger.error(f"❌ Word timing failed: {e}")

    # ── Fallback timing ───────────────────────────────────────────────────────
    if not word_timings:
        logger.warning("⚠️ Using estimated timing fallback")
        current_time = 0.0
        for word in text_script.split():
            dur = 0.38 if len(word) > 5 else 0.28
            word_timings.append({
                "word":  word,
                "start": round(current_time, 3),
                "end":   round(current_time + dur, 3)
            })
            current_time += dur + 0.04

    # ── Real audio duration ───────────────────────────────────────────────────
    try:
        from moviepy.editor import AudioFileClip
        real_duration = AudioFileClip(str(target_audio_path)).duration
    except:
        real_duration = word_timings[-1]["end"] if word_timings else 30.0

    logger.info(f"🎙️ Done | Duration: {real_duration:.2f}s | Words: {len(word_timings)}")

    return {
        "audio_path":   str(target_audio_path),
        "word_timings": word_timings,
        "duration":     real_duration
}
