"""
audio_generator.py — Voiceover Synthesis Engine (SUSPENSE PACING SPEED FIXED)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import logging
import json
import os
import asyncio
from pathlib import Path
import edge_tts
from moviepy.editor import AudioFileClip
import config

logger = logging.getLogger(__name__)

# Premium Deep Dark Voice Setup
VOICE_NAME = "en-US-ChristopherNeural" 
AUDIO_OUTPUT_DIR = Path("output/audio")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_voiceover(script: str, output_stem: str) -> dict:
    """
    Given a script string, synthesizes a slow, suspenseful dark voiceover
    and extracts word-level timings using edge-tts.
    """
    logger.info("Initializing Edge-TTS audio synthesis engine...")
    audio_path = AUDIO_OUTPUT_DIR / f"{output_stem}.mp3"
    
    # 🧪 Clean Script: Extra characters aur breaks hatao
    clean_text = script.replace("\n", " ").replace("  ", " ").strip()
    
    # 🔥 FIX VOICE SPEED (Pacing Tuning):
    # '-12%' karne se voice slow, gehri aur heavy ho jayegi jo suspense videos ke liye perfect hai.
    voice_rate = "-12%" 

    # Run the async text-to-speech process
    asyncio.run(_synthesize_audio_edge(clean_text, str(audio_path), voice_rate))

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise RuntimeError("Edge-TTS failed to generate a valid audio file.")

    # Calculate actual duration using MoviePy
    audio_clip = AudioFileClip(str(audio_path))
    duration_sec = audio_clip.duration
    audio_clip.close()
    
    logger.info(f"✅ Voiceover generated successfully ({duration_sec:.2f}s) -> {audio_path.name}")

    # Step 2: Generate dynamic word timings based on slow pacing
    word_timings = _extract_word_timings_simulated(clean_text, duration_sec)

    return {
        "audio_path": str(audio_path),
        "duration_sec": duration_sec,
        "word_timings": word_timings
    }


async def _synthesize_audio_edge(text: str, output_path: str, rate: str):
    """Internal Edge-TTS execution with specific rate control."""
    communicate = edge_tts.Communicate(text, VOICE_NAME, rate=rate)
    await communicate.save(output_path)


def _extract_word_timings_simulated(text: str, total_duration: float) -> list[dict]:
    """Generates precise time-stamps adjusted for the slower speech rate."""
    words = text.split()
    total_words = len(words)
    
    if total_words == 0:
        return []

    # Dynamic delay simulation adjusted for slow voiceover
    avg_word_dur = total_duration / total_words
    word_timings = []
    current_time = 0.0

    for i, word in enumerate(words):
        # clean word for display
        cleaned_word = word.strip(".,!?;:()\"'")
        if not cleaned_word:
            cleaned_word = word

        start_time = current_time
        # Halka sa variation taake har lafz barabar length ka na lage (natural layout)
        word_len_factor = len(cleaned_word) / 5.0
        word_dur = avg_word_dur * (0.7 + 0.6 * word_len_factor)
        
        end_time = min(start_time + word_dur, total_duration)
        
        # Last word stretch fix
        if i == total_words - 1:
            end_time = total_duration

        word_timings.append({
            "word": cleaned_word,
            "start": round(start_time, 2),
            "end": round(end_time, 2)
        })
        current_time = end_time

    return word_timings
