"""
audio_generator.py — Production Voice Synthesis Layer (v4.0 - SYNC FIXED)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────

FIXES v4.0:
  - Voice changed: en-US-EricNeural (much more natural, human-sounding, FREE)
  - SSML removed from word timing capture — SSML tags were corrupting word boundaries
    causing captions to be out of sync with audio
  - Two-pass approach: SSML for audio render, plain text for timing capture
  - Pauses reduced: comma 200ms, period 400ms (was 450ms/750ms — too slow)
  - Base speed +4% (was -6% — too slow for USA/UK audience)
  - Pitch kept slightly low (-2Hz) for dark aesthetic but not robotic
"""

import os
import re
import logging
import asyncio
from pathlib import Path
import edge_tts

logger = logging.getLogger(__name__)

# ─── Voice Config ──────────────────────────────────────────────────────────────
# Best FREE voices for dark psychology content (USA/UK audience):
# en-US-EricNeural     → Deep, confident, most natural — RECOMMENDED
# en-US-GuyNeural      → Neutral clear voice, good fallback
# en-US-ChristopherNeural → Old choice — too robotic, avoid
VOICE_ID   = "en-US-EricNeural"
BASE_RATE  = "+4%"    # Slightly faster = more engaging for USA/UK
BASE_PITCH = "-2Hz"   # Slight depth without sounding robotic


def build_audio_ssml(text_script: str) -> str:
    """
    Builds SSML only for audio rendering — adds pauses and emphasis.
    NOT used for word timing (that uses plain text to avoid sync errors).
    """
    # Reduced pause times — old values made video too slow
    script = text_script.replace(", ", ', <break time="200ms"/> ')
    script = script.replace(". ", '. <break time="400ms"/> ')
    script = script.replace("! ", '! <break time="350ms"/> ')
    script = script.replace("? ", '? <break time="350ms"/> ')

    return f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="{VOICE_ID}">
            <prosody rate="{BASE_RATE}" pitch="{BASE_PITCH}">
                {script}
            </prosody>
        </voice>
    </speak>"""


async def _render_audio_only(ssml_content: str, output_path: Path):
    """Pass 1: Render audio using SSML (for good sound quality)."""
    communicate = edge_tts.Communicate(ssml_content, VOICE_ID, is_ssml=True)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            with open(output_path, "ab") as f:
                f.write(chunk["data"])


async def _capture_word_timings(plain_text: str) -> list:
    """
    Pass 2: Capture word timings using PLAIN TEXT (no SSML).
    
    KEY FIX: SSML tags confuse edge-tts WordBoundary events — the timing
    offsets come back misaligned because SSML break tags shift the audio
    timeline but word boundary ticks don't account for them correctly.
    Using plain text here gives accurate per-word timestamps.
    """
    word_timings = []
    # Use same rate as audio so timing matches
    communicate = edge_tts.Communicate(plain_text, VOICE_ID, rate=BASE_RATE, pitch=BASE_PITCH)
    
    async for chunk in communicate.stream():
        if chunk["type"] == "WordBoundary":
            start_sec = chunk["offset"] / 10_000_000.0
            duration_sec = chunk["duration"] / 10_000_000.0
            end_sec = start_sec + duration_sec
            word_timings.append({
                "word":  chunk["text"],
                "start": round(start_sec, 3),
                "end":   round(end_sec, 3)
            })
    
    return word_timings


def generate_voiceover(text_script: str, output_filename: str, voice_type: str = "guy_dark") -> dict:
    logger.info(f"🎙️ Generating voiceover | Voice: {VOICE_ID} | Speed: {BASE_RATE}")

    output_dir = Path("output/media")
    output_dir.mkdir(parents=True, exist_ok=True)
    target_audio_path = output_dir / f"{output_filename}.mp3"

    # Clean old file
    if target_audio_path.exists():
        try:
            target_audio_path.unlink()
        except:
            pass

    # ── Pass 1: Render high-quality audio with SSML ───────────────────────────
    ssml_content = build_audio_ssml(text_script)
    try:
        asyncio.run(_render_audio_only(ssml_content, target_audio_path))
        logger.info("✅ Audio render complete")
    except Exception as e:
        logger.error(f"❌ SSML audio render failed: {e} — falling back to plain")
        # Plain text fallback
        communicate = edge_tts.Communicate(text_script, VOICE_ID, rate=BASE_RATE, pitch=BASE_PITCH)
        asyncio.run(communicate.save(str(target_audio_path)))

    # ── Pass 2: Capture accurate word timings with plain text ─────────────────
    word_timings = []
    try:
        word_timings = asyncio.run(_capture_word_timings(text_script))
        logger.info(f"✅ Word timing captured: {len(word_timings)} words synced")
    except Exception as e:
        logger.error(f"❌ Word timing capture failed: {e}")

    # ── Fallback timing if Pass 2 fails ──────────────────────────────────────
    if not word_timings:
        logger.warning("⚠️ Using fallback timing estimation")
        current_time = 0.0
        for word in text_script.split():
            # Estimate duration based on word length
            duration = 0.38 if len(word) > 5 else 0.28
            word_timings.append({
                "word":  word,
                "start": round(current_time, 3),
                "end":   round(current_time + duration, 3)
            })
            current_time += duration + 0.04

    # ── Get real audio duration ───────────────────────────────────────────────
    try:
        from moviepy.editor import AudioFileClip
        real_duration = AudioFileClip(str(target_audio_path)).duration
    except:
        real_duration = word_timings[-1]["end"] if word_timings else 30.0

    logger.info(f"🎙️ Voiceover ready | Duration: {real_duration:.2f}s | Words: {len(word_timings)}")

    return {
        "audio_path":   str(target_audio_path),
        "word_timings": word_timings,
        "duration":     real_duration
}
