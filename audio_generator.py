"""
audio_generator.py — Voiceover Synthesis Engine (NUCLEAR HYPNOTIC EDGE-TTS v6.5 - CHRISTOPHER UPDATE)
AI Dark Realities · Short-Form Video Pipeline
Optimized for: 100% Human Score Niche Distribution (USA/UK Focus)
Formula: en-US-ChristopherNeural + Controlled Pacing (-5%) + Deep Authority Pitch (+0Hz Optimized)
─────────────────────────────────────────────────────────────────────────────────────
"""

import logging
import json
import os
import asyncio
import random
import re
from pathlib import Path
import edge_tts
from moviepy.editor import AudioFileClip, CompositeAudioClip
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# Directory Management
AUDIO_OUTPUT_DIR = Path("output/audio")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Human Realism Audio Parameters
ROOM_NOISE_VOLUME = 0.05  # Optimized target amplitude
BREATH_VOLUME = 0.08      # Natural respiratory envelope scale

_REAL_WORD_TIMINGS = []

# Elite Voice profiles mapped exactly to your zero-cost unlimited human blueprint
VOICE_PROFILES = {
    "guy_dark": {
        "name": "en-US-ChristopherNeural", # 🌟 UPGRADED: Absolute alpha narrative engine for Dark Psychology
        "rate": "-5%",                      # Slow, deep, intimidating pacing
        "pitch": "+0Hz"                     # Native frequency locked for maximum vocal clarity
    },
    "guy_classic": {
        "name": "en-US-GuyNeural",
        "rate": "-12%",                     
        "pitch": "-4Hz"                     
    },
    "ryan_uk": {
        "name": "en-GB-RyanNeural",
        "rate": "-5%",                      
        "pitch": "-2Hz"                     
    },
    "andrew_story": {
        "name": "en-US-AndrewNeural",
        "rate": "-4%",                      
        "pitch": "+0Hz"                     
    }
}


def _normalize_text_for_tts(raw_text: str) -> str:
    """
    🌟 NEW PRE-PARSER ENGINE
    Cleans structural text formatting, expands complex script bugs, 
    and locks precise phonetic safety rules to bypass robotic voice clipping.
    """
    text = raw_text.replace("\n", " ")
    
    # Common Groq JSON output grammar bug corrections
    text = re.sub(r'\bspies\b', 'spikes', text, flags=re.IGNORECASE)
    text = re.sub(r'\bloss\b', 'lose', text, flags=re.IGNORECASE)
    text = re.sub(r'\bintrest\b', 'interest', text, flags=re.IGNORECASE)
    
    # Smooth handling for dramatic pause blocks
    text = text.replace("... WAIT. ...", ", WAIT, ").replace("... WAIT ...", ", WAIT, ")
    text = text.replace("...WAIT...", ", WAIT, ").replace("..WAIT..", ", WAIT, ")
    
    # Strip unnecessary trailing artifacts while preserving breathing anchors
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_voiceover(script: str, output_stem: str, voice_type: str = "guy_dark") -> dict:
    """
    Generates ultra-high retention humanized voiceovers using specific niche blueprints.
    Available voice_type tokens: 'guy_dark' (Christopher Master), 'guy_classic', 'ryan_uk', 'andrew_story'
    """
    logger.info(f"🎙️ Initializing Nuclear Voice Engine using profile token: [{voice_type}]")
    audio_path = AUDIO_OUTPUT_DIR / f"{output_stem}.mp3"

    # Route script text through formatting normalization logic
    clean_text = _normalize_text_for_tts(script)
    
    # Resolve requested voice metadata profiles
    profile = VOICE_PROFILES.get(voice_type, VOICE_PROFILES["guy_dark"])
    selected_voice = profile["name"]
    selected_rate = profile["rate"]
    selected_pitch = profile["pitch"]

    logger.info(f"🚀 Deploying Edge-TTS Pipeline -> Voice: {selected_voice} | Rate: {selected_rate} | Pitch: {selected_pitch}")
    
    # Run asynchronous TTS generation loop
    asyncio.run(_synthesize_audio_edge(clean_text, str(audio_path), selected_voice, selected_rate, selected_pitch))

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise RuntimeError("Edge-TTS engine failed to produce a valid audio asset block.")

    # Apply back-end organic elements layer (Room noise + breaths)
    final_audio_path = _add_human_effects(str(audio_path), output_stem)

    # Calculate actual output time footprints
    audio_clip = AudioFileClip(final_audio_path)
    duration_sec = audio_clip.duration
    audio_clip.close()

    # Extract clean timeline boundary rules for subtitles generator
    word_timings = _extract_word_timings_real(clean_text, duration_sec)

    return {
        "audio_path": final_audio_path,
        "duration_sec": duration_sec,
        "word_timings": word_timings
    }


async def _synthesize_audio_edge(text: str, output_path: str, voice: str, rate: str, pitch: str):
    global _REAL_WORD_TIMINGS
    _REAL_WORD_TIMINGS = [] 
    
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    
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
    """Injects high-fidelity room environment models and respiratory sound anchors."""
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

    try:
        os.remove(audio_path)
    except Exception:
        pass

    return str(output_path)


def _generate_room_noise(duration: float):
    fps = 44100
    n_samples = int(duration * fps)
    noise = np.random.normal(0, 0.0015, (n_samples, 2))  # Smooth, subtle studio air frequency
    return AudioArrayClip(noise, fps=fps).volumex(ROOM_NOISE_VOLUME)


def _generate_breath_sounds(duration: float):
    fps = 44100
    n_samples = int(duration * fps)
    breath_track = np.zeros((n_samples, 2))

    current_time = random.uniform(6, 10)  # Human respiration frequency anchor points
    while current_time < duration:
        start_sample = int(current_time * fps)
        breath_len = int(0.22 * fps)

        if start_sample + breath_len < n_samples:
            t = np.linspace(0, 0.22, breath_len)
            breath = np.sin(2 * np.pi * 80 * t) * np.exp(-7 * t) * 0.06
            breath_track[start_sample:start_sample+breath_len, 0] = breath
            breath_track[start_sample:start_sample+breath_len, 1] = breath

        current_time += random.uniform(9, 14)

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

        # Force structural retention hold-lock on suspense anchors
        if raw_word.upper() == "WAIT":
            end = start + 1.2
            accumulated_delay += 1.2 
            
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
            # Precise alignment tuning factors to keep visual word frames tightly focused
            adjusted_start = max(0.0, adjusted_start - 0.05)
            adjusted_end = max(0.0, adjusted_end - 0.02)

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
        if cleaned_word.upper() == "WAIT": word_dur = 1.2
        end_time = start_time + word_dur
        if end_time > total_duration or i == total_words - 1: end_time = total_duration
        word_timings.append({"word": cleaned_word if cleaned_word.upper() != "WAIT" else "WAIT...", "start": round(start_time, 2), "end": round(end_time, 2)})
        current_time = end_time
    return word_timings
