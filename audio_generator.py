"""
audio_generator.py — Production Voice Synthesis Layer (v6.0)
AI Dark Realities · High Retention Edition
"""

import re
import subprocess
import logging
import asyncio
import shutil
from pathlib import Path
import edge_tts

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# Voice Config
# ─────────────────────────────────────────
VOICE_ID = "en-US-BrianMultilingualNeural"
BASE_RATE = "+12%"
BASE_PITCH = "0Hz"

# ─────────────────────────────────────────
# Audio Master Filter
# ─────────────────────────────────────────
PODCAST_FILTER = (
    "highpass=f=80,"
    "lowpass=f=9000,"
    "equalizer=f=120:width_type=o:width=2:g=2,"
    "equalizer=f=3000:width_type=o:width=2:g=1,"
    "equalizer=f=5000:width_type=o:width=2:g=-2,"
    "acompressor=threshold=-18dB:ratio=2:attack=5:release=50,"
    "loudnorm"
)


def apply_podcast_filter(input_path: Path, output_path: Path):
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-af",
                PODCAST_FILTER,
                "-acodec",
                "libmp3lame",
                "-q:a",
                "2",
                str(output_path)
            ],
            capture_output=True,
            timeout=60
        )

        if (
            result.returncode == 0
            and output_path.exists()
            and output_path.stat().st_size > 1000
        ):
            logger.info("✅ Audio mastered successfully")
            return True

        logger.warning("⚠️ Filter failed. Using raw audio.")
        return False

    except Exception as e:
        logger.warning(f"⚠️ FFmpeg Error: {e}")
        return False


def generate_voiceover(
    text_script: str,
    output_filename: str,
    voice_type: str = "dark"
):

    logger.info("🎙️ Generating Voice...")

    output_dir = Path("output/media")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_audio_path = output_dir / f"{output_filename}_raw.mp3"
    target_audio_path = output_dir / f"{output_filename}.mp3"

    for p in [raw_audio_path, target_audio_path]:
        if p.exists():
            p.unlink(missing_ok=True)

    # Natural pauses
    text_script = text_script.replace(".", "... ")
    text_script = text_script.replace("!", "! ... ")
    text_script = text_script.replace("?", "? ... ")

    # Better cleaning
    clean_text_stream = re.sub(
        r'[^\w\s\.,!\?\'":;\-]',
        '',
        text_script
    )

    clean_text_stream = " ".join(
        clean_text_stream.strip().split()
    )

    word_timings = []

    async def render_audio():

        communicate = edge_tts.Communicate(
            clean_text_stream,
            VOICE_ID,
            rate=BASE_RATE,
            pitch=BASE_PITCH
        )

        async for chunk in communicate.stream():

            if chunk["type"] == "audio":
                with open(raw_audio_path, "ab") as f:
                    f.write(chunk["data"])

            elif chunk["type"] == "WordBoundary":

                text_word = chunk.get("text", "")

                if text_word:

                    start = chunk.get(
                        "offset",
                        0
                    ) / 10_000_000.0

                    duration = chunk.get(
                        "duration",
                        0
                    ) / 10_000_000.0

                    word_timings.append(
                        {
                            "word": text_word.upper(),
                            "start": round(start, 3),
                            "end": round(
                                start + duration,
                                3
                            )
                        }
                    )

    try:
        asyncio.run(render_audio())
        logger.info(
            f"✅ Boundaries received: {len(word_timings)}"
        )

    except Exception as e:
        logger.error(f"❌ TTS Error: {e}")

    # Audio mastering
    success = apply_podcast_filter(
        raw_audio_path,
        target_audio_path
    )

    if not success:
        shutil.copy(
            str(raw_audio_path),
            str(target_audio_path)
        )

    raw_audio_path.unlink(missing_ok=True)

    # Duration
    try:
        from moviepy.editor import AudioFileClip

        real_duration = AudioFileClip(
            str(target_audio_path)
        ).duration

    except Exception:
        real_duration = (
            word_timings[-1]["end"]
            if word_timings
            else 30.0
        )

    # Fallback timings
    if not word_timings:

        current_time = 0

        for word in clean_text_stream.split():

            dur = max(
                0.18,
                len(word) * 0.045
            )

            word_timings.append(
                {
                    "word": word.upper(),
                    "start": round(current_time, 3),
                    "end": round(
                        current_time + dur,
                        3
                    )
                }
            )

            current_time += dur + 0.05

    # Caption cutoff
    safe_cutoff_mark = max(
        0,
        real_duration - 1.5
    )

    word_timings = [
        x
        for x in word_timings
        if x["start"] < safe_cutoff_mark
    ]

    # ───────────────────────────
    # Convert to phrase captions
    # ───────────────────────────
    phrase_timings = []

    i = 0

    while i < len(word_timings):

        group = word_timings[i:i + 3]

        text = " ".join(
            w["word"] for w in group
        )

        phrase_timings.append(
            {
                "word": text,
                "start": group[0]["start"],
                "end": group[-1]["end"]
            }
        )

        i += 3

    logger.info(
        f"✅ Phrase captions: {len(phrase_timings)}"
    )

    return {
        "audio_path": str(
            target_audio_path
        ),
        "word_timings": phrase_timings,
        "duration": real_duration
    }
