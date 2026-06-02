"""
audio_generator.py — Voiceover Synthesis Engine (HUMAN MODE + PERFECT SYNC v3.1)
AI Dark Realities · Short-Form Video Pipeline
Fixed: SubMaker AttributeError resolved via direct chunk boundary mapping
──────────────────────────────────────────────
"""

import logging
import json
import os
import asyncio
import random
from pathlib import Path
import edge_tts
from moviepy.editor import AudioFileClip, CompositeAudioClip
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np
import config

logger = logging.getLogger(__name__)

# Premium Deep Dark Voice Setup
VOICE_NAME = "en-US-ChristopherNeural"
AUDIO_OUTPUT_DIR = Path("output/audio")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Human Mode Settings
PAUSE_PROBABILITY = 0.15  # 15% chance har 8-12 words pe pause
ROOM_NOISE_VOLUME = 0.08  # 8% volume pe background noise
BREATH_VOLUME = 0.15  # Saans ki awaz

# Global variable for real word timings
_REAL_WORD_TIMINGS = []

def generate_voiceover(script: str, output_stem: str) -> dict:
    """
    Human-like voiceover with REAL word timings from Edge-TTS
    Returns: audio_path, duration, word_timings - 100% sync
    """
    logger.info("Initializing Human Mode TTS with Real Sync...")
    audio_path = AUDIO_OUTPUT_DIR / f"{output_stem}.mp3"

    # Step 1: Script me human pauses + filler words inject karo
    human_script = _add_human_pauses(script)

    # Step 2: TTS + Real timings generate karo
    clean_text = human_script.replace("\n", " ").replace("  ", " ").strip()
    voice_rate = "-10%"  # Thora slow/deep = human

    asyncio.run(_synthesize_audio_edge(clean_text, str(audio_path), voice_rate))

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise RuntimeError("Edge-TTS failed to generate a valid audio file.")

    # Step 3: Room noise + breath add karo
    final_audio_path = _add_human_effects(str(audio_path), output_stem)

    # Duration nikalo
    audio_clip = AudioFileClip(final_audio_path)
    duration_sec = audio_clip.duration
    audio_clip.close()

    logger.info(f"✅ Human voiceover generated: {duration_sec:.2f}s")

    # Step 4: REAL word timings use karo - guess nahi
    word_timings = _extract_word_timings_real(clean_text, duration_sec)

    return {
        "audio_path": final_audio_path,
        "duration_sec": duration_sec,
        "word_timings": word_timings
    }

async def _synthesize_audio_edge(text: str, output_path: str, rate: str):
    """Edge-TTS with REAL word timings captured directly from boundary chunks"""
    global _REAL_WORD_TIMINGS
    _REAL_WORD_TIMINGS = [] # Reset global list before generation
    
    pitch_variation = random.randint(-2, 2)
    pitch = f"{pitch_variation:+}Hz" 

    communicate = edge_tts.Communicate(text, VOICE_NAME, rate=rate, pitch=pitch)
    
    with open(output_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # 🔥 FIXED: Capture boundary data directly from the stream chunks
                # structure: {"type": "WordBoundary", "offset": int, "duration": int, "text": str}
                _REAL_WORD_TIMINGS.append({
                    "offset": chunk["offset"],
                    "duration": chunk["duration"],
                    "text": chunk["text"]
                })
    
    logger.info(f"Captured {len(_REAL_WORD_TIMINGS)} real word timings from Edge-TTS stream")

def _add_human_pauses(script: str) -> str:
    """
    Har 8-12 words ke baad random pause... add karta hai
    "umm, like, right" wale filler bhi inject karta hai
    """
    words = script.split()
    result = []
    word_count = 0
    filler_words = ["umm", "like", "you know", "right", "actually"]

    for i, word in enumerate(words):
        result.append(word)
        word_count += 1

        # Har 8-12 words pe pause check
        if word_count >= random.randint(8, 12):
            if random.random() < PAUSE_PROBABILITY:
                if random.random() < 0.7:
                    result.append("...")
                else:
                    result.append(random.choice(filler_words) + "...")
            word_count = 0

    return " ".join(result)

def _add_human_effects(audio_path: str, output_stem: str) -> str:
    """
    Room noise + breath sound add karta hai taake AI na lage
    Volume halka up-down = saans lene jesa effect
    """
    main_audio = AudioFileClip(audio_path)
    duration = main_audio.duration

    # 1. Halka room noise generate karo
    room_noise = _generate_room_noise(duration)

    # 2. Random breath sounds har 15-20 sec pe
    breath_audio = _generate_breath_sounds(duration)

    # 3. Sab combine karo
    final_audio = CompositeAudioClip([main_audio, room_noise, breath_audio])

    # Volume modulation for breathing feeling
    final_audio = final_audio.volumex(lambda t: 0.96 + 0.04 * np.sin(t * 0.4))

    output_path = AUDIO_OUTPUT_DIR / f"{output_stem}_human.mp3"
    final_audio.write_audiofile(
        str(output_path),
        fps=44100,
        codec="mp3",
        bitrate="128k",
        logger=None
    )

    main_audio.close()
    room_noise.close()
    breath_audio.close()

    try:
        os.remove(audio_path)
    except Exception:
        pass

    return str(output_path)

def _generate_room_noise(duration: float):
    """Halka AC/Fan noise - bilkul silence AI lagta hai"""
    fps = 44100
    n_samples = int(duration * fps)
    noise = np.random.normal(0, 0.003, (n_samples, 2))
    return AudioArrayClip(noise, fps=fps).volumex(ROOM_NOISE_VOLUME)

def _generate_breath_sounds(duration: float):
    """Har 15-20 sec pe halki saans ki awaz"""
    fps = 44100
    n_samples = int(duration * fps)
    breath_track = np.zeros((n_samples, 2))

    current_time = random.uniform(10, 15)
    while current_time < duration:
        start_sample = int(current_time * fps)
        breath_len = int(0.3 * fps)

        if start_sample + breath_len < n_samples:
            t = np.linspace(0, 0.3, breath_len)
            breath = np.sin(2 * np.pi * 80 * t) * np.exp(-5 * t) * 0.1
            breath_track[start_sample:start_sample+breath_len, 0] = breath
            breath_track[start_sample:start_sample+breath_len, 1] = breath

        current_time += random.uniform(15, 20)

    return AudioArrayClip(breath_track, fps=fps).volumex(BREATH_VOLUME)

def _extract_word_timings_real(text: str, total_duration: float) -> list:
    """
    REAL word timings Edge-TTS se - 100% sync
    Agar timings na mile to fallback
    """
    global _REAL_WORD_TIMINGS
    
    if not _REAL_WORD_TIMINGS:
        logger.warning("Real timings not found, using simulated fallback")
        return _extract_word_timings_simulated(text, total_duration)
    
    word_timings = []
    for word_obj in _REAL_WORD_TIMINGS:
        word = word_obj["text"].strip(".,!?;:()\"'")
        if word and word.lower() not in ["umm", "like", "right", "actually", "you", "know"]:
            # Edge-TTS gives time in 100-nanoseconds ticks
            start = word_obj["offset"] / 10_000_000.0
            end = start + (word_obj["duration"] / 10_000_000.0)
            
            if end > total_duration:
                end = total_duration
            
            word_timings.append({
                "word": word,
                "start": round(start, 2),
                "end": round(end, 2)
            })
    
    logger.info(f"Using {len(word_timings)} real word timings for captions")
    return word_timings

def _extract_word_timings_simulated(text: str, total_duration: float) -> list:
    """Fallback: Agar Edge-TTS timing na de to ye use hoga"""
    clean_words_only = text.replace("...", " ").replace("umm", "").replace("like", "").replace("right", "").replace("you know", "").replace("actually", "")
    words = clean_words_only.split()
    total_words = len(words)

    if total_words == 0:
        return []

    avg_word_dur = total_duration / total_words
    word_timings = []
    current_time = 0.0

    for i, word in enumerate(words):
        cleaned_word = word.strip(".,!?;:()\"'")
        if not cleaned_word:
            cleaned_word = word

        start_time = current_time
        word_len_factor = len(cleaned_word) / 5.0
        word_dur = avg_word_dur * (0.8 + 0.4 * word_len_factor)
        end_time = start_time + word_dur

        if end_time > total_duration or i == total_words - 1:
            end_time = total_duration

        word_timings.append({
            "word": cleaned_word,
            "start": round(start_time, 2),
            "end": round(end_time, 2)
        })
        current_time = end_time

    return word_timings
