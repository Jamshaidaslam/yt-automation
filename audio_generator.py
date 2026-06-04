"""
audio_generator.py — Voice Engine (STABLE)
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

ROOM_NOISE_VOLUME = 0.04
BREATH_VOLUME     = 0.08
BG_MUSIC_VOLUME   = 0.06

VOICE_PROFILES = {
    "guy_dark": ("en-US-GuyNeural",   "-12Hz"),
    "ryan_uk":  ("en-GB-RyanNeural",  "-9Hz"),
    "main_voice": ("en-US-GuyNeural", "-12Hz"),   # BUG FIX 1: "main_voice" key missing tha
}


# ══════════════════════════════════════════════════════════════════════════════
def generate_voiceover(script: str, output_stem: str, voice_type: str = "guy_dark") -> dict:
    """
    Returns:
        {
            "audio_path":    str,
            "duration_sec":  float,
            "text":          str,
            "word_timings":  list[{"word": str, "start": float, "end": float}]
        }
    """
    audio_path = AUDIO_OUTPUT_DIR / f"{output_stem}.mp3"

    # BUG FIX 2: Unknown voice_type → fallback instead of KeyError crash
    profile = VOICE_PROFILES.get(voice_type, VOICE_PROFILES["guy_dark"])
    voice_name, pitch = profile

    rate  = f"-{random.randint(4, 7)}%"
    words_with_timing = []

    # ── Retry logic ──────────────────────────────────────────────────────────
    for attempt in range(3):
        try:
            words_with_timing = asyncio.run(
                _synthesize_with_timing(script, str(audio_path), voice_name, rate, pitch)
            )
            if audio_path.exists() and audio_path.stat().st_size > 2000:
                break
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == 2:
                raise RuntimeError(f"Voice generation failed after 3 attempts: {e}")

    # ── Human effects ─────────────────────────────────────────────────────────
    final_audio_path = _add_human_effects(str(audio_path), output_stem)

    # ── Duration ──────────────────────────────────────────────────────────────
    audio_clip = AudioFileClip(final_audio_path)
    dur = audio_clip.duration
    audio_clip.close()

    logger.info(f"✅ Voiceover ready: {final_audio_path} ({dur:.1f}s, {len(words_with_timing)} words)")

    return {
        "audio_path":   final_audio_path,
        "duration_sec": dur,
        "text":         script,
        "word_timings": words_with_timing,   # BUG FIX 3: yeh pehle return nahi hota tha
    }


# ══════════════════════════════════════════════════════════════════════════════
async def _synthesize_with_timing(text: str, output_path: str,
                                   voice: str, rate: str, pitch: str) -> list:
    """
    Synthesize audio AND collect word-level timing from edge-tts WordBoundary events.
    Returns list of {"word": str, "start": float, "end": float}
    """
    text = text.replace("... WAIT. ...", ", WAIT, ")

    communicate   = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    word_timings  = []
    audio_chunks  = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])

        elif chunk["type"] == "WordBoundary":
            # edge-tts gives offset in 100-nanosecond units
            start_sec = chunk["offset"]   / 10_000_000
            dur_sec   = chunk["duration"] / 10_000_000
            word_timings.append({
                "word":  chunk["text"],
                "start": round(start_sec, 3),
                "end":   round(start_sec + dur_sec, 3),
            })

    with open(output_path, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    return word_timings


# ══════════════════════════════════════════════════════════════════════════════
def _add_human_effects(audio_path: str, output_stem: str) -> str:
    main_audio = AudioFileClip(audio_path)
    dur        = main_audio.duration
    components = [
        main_audio,
        _generate_room_noise(dur),
        _generate_breath_sounds(dur),
    ]

    if MUSIC_ASSETS_DIR.exists():
        files = [f for f in MUSIC_ASSETS_DIR.iterdir() if f.suffix in (".mp3", ".wav")]
        if files:
            try:
                bgm_clip = AudioFileClip(str(random.choice(files)))
                bgm      = audio_loop(bgm_clip, duration=dur).volumex(BG_MUSIC_VOLUME)
                components.append(bgm)
            except Exception as e:
                logger.warning(f"BGM load failed: {e}")

    final = CompositeAudioClip(components).set_duration(dur)
    out   = AUDIO_OUTPUT_DIR / f"{output_stem}_human.mp3"

    final.write_audiofile(
        str(out), fps=44100, codec="mp3", bitrate="192k", logger=None
    )

    main_audio.close()
    final.close()

    try:
        os.remove(audio_path)
    except Exception:
        pass

    return str(out)


# ══════════════════════════════════════════════════════════════════════════════
def _generate_room_noise(duration: float):
    fps   = 44100
    noise = np.random.normal(0, 0.002, (int(duration * fps), 2))
    return AudioArrayClip(noise, fps=fps).volumex(ROOM_NOISE_VOLUME)


def _generate_breath_sounds(duration: float):
    fps         = 44100
    breath_track = np.zeros((int(duration * fps), 2))
    curr        = random.uniform(6, 10)

    while curr < duration:
        start      = int(curr * fps)
        breath_len = int(0.24 * fps)
        if start + breath_len < len(breath_track):
            t      = np.linspace(0, 0.24, breath_len)
            breath = np.sin(2 * np.pi * 75 * t) * np.exp(-6 * t) * 0.08
            breath_track[start:start + breath_len] = breath.reshape(-1, 1)
        curr += random.uniform(8, 14)

    return AudioArrayClip(breath_track, fps=fps).volumex(BREATH_VOLUME)
