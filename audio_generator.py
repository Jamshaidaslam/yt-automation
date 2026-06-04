"""
audio_generator.py — Nuclear Voice Engine (v6.7 STABLE - 3-VIDEOS-A-DAY READY)
Fixes: 
  1. Added multi-attempt retry logic for API resilience.
  2. Byte-size verification to prevent corrupt audio uploads.
  3. Seamless integration for human-organic background layers.
"""

import logging
import asyncio
import random
from pathlib import Path
import edge_tts
from moviepy.editor import AudioFileClip, CompositeAudioClip
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np
import os

logger = logging.getLogger(__name__)

AUDIO_OUTPUT_DIR = Path("output/audio")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_ASSETS_DIR = Path("assets/music")

ROOM_NOISE_VOLUME = 0.04
BREATH_VOLUME = 0.08
BG_MUSIC_VOLUME = 0.07

_REAL_WORD_TIMINGS = []

VOICE_PROFILES = {
    "guy_dark": {"name": "en-US-GuyNeural", "pitch": "-12Hz"},
    "ryan_uk": {"name": "en-GB-RyanNeural", "pitch": "-9Hz"}
}

def generate_voiceover(script: str, output_stem: str, voice_type: str = "guy_dark") -> dict:
    audio_path = AUDIO_OUTPUT_DIR / f"{output_stem}.mp3"
    clean_text = script.replace("\n", " ").replace("  ", " ").strip()
    profile = VOICE_PROFILES.get(voice_type, VOICE_PROFILES["guy_dark"])
    
    # 🔥 CRITICAL: Retry logic for 3-video-a-day network reliability
    max_retries = 3
    for attempt in range(max_retries):
        try:
            asyncio.run(_synthesize_audio_edge(clean_text, str(audio_path), profile["name"], f"-{random.randint(4, 7)}%", profile["pitch"]))
            if audio_path.exists() and audio_path.stat().st_size > 2000: # Check if file is valid
                break
        except Exception as e:
            if attempt == max_retries - 1: raise RuntimeError(f"Voice engine failed after {max_retries} attempts: {e}")
            logger.warning(f"Voice generation attempt {attempt+1} failed, retrying...")

    final_audio_path = _add_human_effects(str(audio_path), output_stem)

    audio_clip = AudioFileClip(final_audio_path)
    duration_sec = audio_clip.duration
    audio_clip.close()

    word_timings = _extract_word_timings_real(clean_text, duration_sec)

    return {"audio_path": final_audio_path, "duration_sec": duration_sec, "word_timings": word_timings}

async def _synthesize_audio_edge(text: str, output_path: str, voice: str, rate: str, pitch: str):
    global _REAL_WORD_TIMINGS
    _REAL_WORD_TIMINGS = [] 
    
    tts_text = text.replace("... WAIT. ...", ", WAIT, ").replace("... WAIT ...", ", WAIT, ")
    communicate = edge_tts.Communicate(tts_text, voice, rate=rate, pitch=pitch)
    
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
    audio_components = [main_audio, _generate_room_noise(duration), _generate_breath_sounds(duration)]

    if MUSIC_ASSETS_DIR.exists():
        music_files = [f for f in MUSIC_ASSETS_DIR.iterdir() if f.suffix.lower() in ['.mp3', '.wav', '.m4a']]
        if music_files:
            bg_music_clip = AudioFileClip(str(random.choice(music_files))).loop(duration=duration).volumex(BG_MUSIC_VOLUME)
            audio_components.append(bg_music_clip)

    final_audio = CompositeAudioClip(audio_components).set_duration(duration)
    output_path = AUDIO_OUTPUT_DIR / f"{output_stem}_human.mp3"
    
    final_audio.write_audiofile(str(output_path), fps=44100, codec="mp3", bitrate="192k", logger=None)
    main_audio.close()
    final_audio.close()
    try: os.remove(audio_path)
    except: pass
    return str(output_path)

def _generate_room_noise(duration: float):
    fps = 44100
    noise = np.random.normal(0, 0.002, (int(duration * fps), 2))
    return AudioArrayClip(noise, fps=fps).volumex(ROOM_NOISE_VOLUME)

def _generate_breath_sounds(duration: float):
    fps = 44100
    breath_track = np.zeros((int(duration * fps), 2))
    current_time = random.uniform(6, 10)
    while current_time < duration:
        start = int(current_time * fps)
        breath_len = int(0.24 * fps)
        if start + breath_len < len(breath_track):
            t = np.linspace(0, 0.24, breath_len)
            breath = np.sin(2 * np.pi * 75 * t) * np.exp(-6 * t) * 0.08
            breath_track[start:start+breath_len] = breath.reshape(-1, 1)
        current_time += random.uniform(8, 14)
    return AudioArrayClip(breath_track, fps=fps).volumex(BREATH_VOLUME)

def _extract_word_timings_real(text: str, total_duration: float) -> list:
    global _REAL_WORD_TIMINGS
    if not _REAL_WORD_TIMINGS: return _extract_word_timings_simulated(text, total_duration)
    
    raw_timings = []
    acc_delay = 0.0
    for w in _REAL_WORD_TIMINGS:
        start = (w["offset"] / 10_000_000.0) + acc_delay
        end = start + (w["duration"] / 10_000_000.0)
        word = w["text"].strip(".,!?;:()\"'")
        if word.upper() == "WAIT": end += 1.5; acc_delay += 1.5
        raw_timings.append({"word": word, "start": start, "end": end})
    
    speed_factor = total_duration / raw_timings[-1]["end"] if raw_timings else 1.0
    return [{"word": t["word"], "start": round(t["start"] * speed_factor, 2), "end": round(t["end"] * speed_factor, 2)} for t in raw_timings]

def _extract_word_timings_simulated(text: str, total_duration: float) -> list:
    words = text.split()
    avg = total_duration / len(words) if words else 0
    return [{"word": w.strip(".,!?;:()\"'"), "start": round(i*avg, 2), "end": round((i+1)*avg, 2)} for i, w in enumerate(words)]
