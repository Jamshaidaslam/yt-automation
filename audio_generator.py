"""
audio_generator.py — Nuclear Voice Engine (v6.8 STABLE)
"""

import logging, asyncio, random, os
from pathlib import Path
import edge_tts
from moviepy.editor import AudioFileClip, CompositeAudioClip
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy.audio.fx.all import audio_loop
import numpy as np

logger = logging.getLogger(__name__)

AUDIO_OUTPUT_DIR = Path("output/audio")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_ASSETS_DIR = Path("assets/music")

# Human Organic Effects
ROOM_NOISE_VOLUME = 0.04
BREATH_VOLUME = 0.08
BG_MUSIC_VOLUME = 0.06

def generate_voiceover(script, output_stem, voice_type="guy_dark"):
    audio_path = AUDIO_OUTPUT_DIR / f"{output_stem}.mp3"
    profile = {"guy_dark": ("en-US-GuyNeural", "-12Hz"), "ryan_uk": ("en-GB-RyanNeural", "-9Hz")}.get(voice_type)
    
    # Retry logic for stability
    for attempt in range(3):
        try:
            asyncio.run(_synthesize_audio_edge(script, str(audio_path), profile[0], f"-{random.randint(4,7)}%", profile[1]))
            if audio_path.exists() and audio_path.stat().st_size > 2000: break
        except Exception as e:
            if attempt == 2: raise RuntimeError(f"Voice generation failed: {e}")
            
    final_audio_path = _add_human_effects(str(audio_path), output_stem)
    
    audio_clip = AudioFileClip(final_audio_path)
    dur = audio_clip.duration
    audio_clip.close()
    
    return {"audio_path": final_audio_path, "duration_sec": dur}

async def _synthesize_audio_edge(text, output_path, voice, rate, pitch):
    text = text.replace("... WAIT. ...", ", WAIT, ")
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    with open(output_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio": file.write(chunk["data"])

def _add_human_effects(audio_path, output_stem):
    main_audio = AudioFileClip(audio_path)
    dur = main_audio.duration
    components = [main_audio, _generate_room_noise(dur), _generate_breath_sounds(dur)]
    
    if MUSIC_ASSETS_DIR.exists():
        files = [f for f in MUSIC_ASSETS_DIR.iterdir() if f.suffix in ['.mp3', '.wav']]
        if files:
            # FIX: audio_loop use kiya hai yahan
            bgm = audio_loop(AudioFileClip(str(random.choice(files))), duration=dur).volumex(BG_MUSIC_VOLUME)
            components.append(bgm)
            
    final = CompositeAudioClip(components).set_duration(dur)
    out = AUDIO_OUTPUT_DIR / f"{output_stem}_human.mp3"
    final.write_audiofile(str(out), fps=44100, codec="mp3", bitrate="192k", logger=None)
    
    main_audio.close()
    final.close()
    try: os.remove(audio_path)
    except: pass
    return str(out)

def _generate_room_noise(duration):
    fps = 44100
    noise = np.random.normal(0, 0.002, (int(duration * fps), 2))
    return AudioArrayClip(noise, fps=fps).volumex(ROOM_NOISE_VOLUME)

def _generate_breath_sounds(duration):
    fps = 44100
    breath_track = np.zeros((int(duration * fps), 2))
    curr = random.uniform(6, 10)
    while curr < duration:
        start = int(curr * fps)
        breath_len = int(0.24 * fps)
        if start + breath_len < len(breath_track):
            t = np.linspace(0, 0.24, breath_len)
            breath = np.sin(2 * np.pi * 75 * t) * np.exp(-6 * t) * 0.08
            breath_track[start:start+breath_len] = breath.reshape(-1, 1)
        curr += random.uniform(8, 14)
    return AudioArrayClip(breath_track, fps=fps).volumex(BREATH_VOLUME)
