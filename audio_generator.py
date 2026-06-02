"""
audio_generator.py — Voiceover Synthesis Engine (GLITCH FREE SYNC v5.0)
AI Dark Realities · Short-Form Video Pipeline
Fixed: Preserves timeline alignment when dense filler structures are filtered out.
Fixed: Enforced proper timing allocation for the automated silence frame window.
Tested: Fully compatible with GitHub Actions and Python 3.10+ environments.
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

VOICE_NAME = "en-US-ChristopherNeural"
AUDIO_OUTPUT_DIR = Path("output/audio")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAUSE_PROBABILITY = 0.10  
ROOM_NOISE_VOLUME = 0.08  
BREATH_VOLUME = 0.12  

_REAL_WORD_TIMINGS = []

def generate_voiceover(script: str, output_stem: str) -> dict:
    logger.info("Initializing Short-Form Glitch-Free Voice Engine...")
    audio_path = AUDIO_OUTPUT_DIR / f"{output_stem}.mp3"

    clean_text = script.replace("\n", " ").replace("  ", " ").strip()
    voice_rate = "-8%"  # Sharp, quick delivery for high engagement retention

    asyncio.run(_synthesize_audio_edge(clean_text, str(audio_path), voice_rate))

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise RuntimeError("Edge-TTS failed to generate a valid audio file.")

    final_audio_path = _add_human_effects(str(audio_path), output_stem)

    audio_clip = AudioFileClip(final_audio_path)
    duration_sec = audio_clip.duration
    audio_clip.close()

    word_timings = _extract_word_timings_real(clean_text, duration_sec)

    return {
        "audio_path": final_audio_path,
        "duration_sec": duration_sec,
        "word_timings": word_timings
    }

async def _synthesize_audio_edge(text: str, output_path: str, rate: str):
    global _REAL_WORD_TIMINGS
    _REAL_WORD_TIMINGS = [] 
    
    pitch_variation = random.randint(-1, 1)
    pitch = f"{pitch_variation:+}Hz" 

    tts_text = text.replace("... WAIT. ...", ", WAIT, ")

    communicate = edge_tts.Communicate(tts_text, VOICE_NAME, rate=rate, pitch=pitch)
    
    with open(output_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                _REAL_WORD_TIMINGS.append({
                    "offset": chunk["offset"],
                    "duration": chunk["duration"],
                    "text": chunk["text"]
                })

def _add_human_effects(audio_path: str, output_stem: str) -> str:
    main_audio = AudioFileClip(audio_path)
    duration = main_audio.duration

    room_noise = _generate_room_noise(duration)
    breath_audio = _generate_breath_sounds(duration)

    final_audio = CompositeAudioClip([main_audio, room_noise, breath_audio])
    final_audio.duration = duration
    final_audio = final_audio.volumex(1.0)

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
    final_audio.close()

    try: os.remove(audio_path)
    except Exception: pass

    return str(output_path)

def _generate_room_noise(duration: float):
    fps = 44100
    n_samples = int(duration * fps)
    noise = np.random.normal(0, 0.003, (n_samples, 2))
    return AudioArrayClip(noise, fps=fps).volumex(ROOM_NOISE_VOLUME)

def _generate_breath_sounds(duration: float):
    fps = 44100
    n_samples = int(duration * fps)
    breath_track = np.zeros((n_samples, 2))

    current_time = random.uniform(10, 15)
    while current_time < duration:
        start_sample = int(current_time * fps)
        breath_len = int(0.25 * fps)

        if start_sample + breath_len < n_samples:
            t = np.linspace(0, 0.25, breath_len)
            breath = np.sin(2 * np.pi * 80 * t) * np.exp(-5 * t) * 0.1
            breath_track[start_sample:start_sample+breath_len, 0] = breath
            breath_track[start_sample:start_sample+breath_len, 1] = breath

        current_time += random.uniform(12, 18)

    return AudioArrayClip(breath_track, fps=fps).volumex(BREATH_VOLUME)

def _extract_word_timings_real(text: str, total_duration: float) -> list:
    global _REAL_WORD_TIMINGS
    
    if not _REAL_WORD_TIMINGS:
        return _extract_word_timings_simulated(text, total_duration)
    
    raw_timings = []
    accumulated_delay = 0.0  

    for word_obj in _REAL_WORD_TIMINGS:
        raw_word = word_obj["text"].strip(".,!?;:()\"'")
        start = (word_obj["offset"] / 10_000_000.0) + accumulated_delay
        end = start + (word_obj["duration"] / 10_000_000.0)
        
        if raw_word.lower() in ["umm", "like", "right", "um", ""]:
            continue

        if raw_word.upper() == "WAIT":
            end = start + 1.5
            accumulated_delay += 1.5 
            
        raw_timings.append({
            "word": raw_word if raw_word.upper() != "WAIT" else "WAIT...",
            "start": start,
            "end": end
        })

    if not raw_timings:
        return _extract_word_timings_simulated(text, total_duration)

    edge_total_duration = raw_timings[-1]["end"]
    speed_factor = total_duration / edge_total_duration if edge_total_duration > 0 else 1.0
    
    word_timings = []
    for item in raw_timings:
        adjusted_start = item["start"] * speed_factor
        adjusted_end = item["end"] * speed_factor
        
        if "WAIT" not in item["word"]:
            adjusted_start = max(0.0, adjusted_start - 0.12)
            adjusted_end = max(0.0, adjusted_end - 0.08)

        if adjusted_end > total_duration:
            adjusted_end = total_duration
            
        word_timings.append({
            "word": item["word"],
            "start": round(adjusted_start, 2),
            "end": round(adjusted_end, 2)
        })
        
    return word_timings

def _extract_word_timings_simulated(text: str, total_duration: float) -> list:
    words = text.split()
    total_words = len(words)
    if total_words == 0: return []
    avg_word_dur = total_duration / total_words
    word_timings = []
    current_time = 0.0
    for i, word in enumerate(words):
        cleaned_word = word.strip(".,!?;:()\"'")
        start_time = current_time
        word_dur = avg_word_dur
        if cleaned_word.upper() == "WAIT": word_dur = 1.5
        end_time = start_time + word_dur
        if end_time > total_duration or i == total_words - 1: end_time = total_duration
        word_timings.append({"word": cleaned_word if cleaned_word.upper() != "WAIT" else "WAIT...", "start": round(start_time, 2), "end": round(end_time, 2)})
        current_time = end_time
    return word_timings
