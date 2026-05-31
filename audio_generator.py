"""
audio_generator.py — High-Retention Natural Male Voice Engine (Edge-TTS + SSML Emotions)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
import edge_tts
from script_generator import build_word_timings
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

def generate_voiceover(script: str, output_stem: str) -> dict:
    final_audio_path = config.AUDIO_DIR / f"{output_stem}.mp3"
    timings_path = config.AUDIO_DIR / f"{output_stem}_timings.json"

    logger.info("Synthesizing high-retention natural male voiceover via Edge Cloud...")

    try:
        if final_audio_path.exists():
            final_audio_path.unlink()

        voice_character = "en-US-ChristopherNeural"

        async def save_voice():
            # SSML se dark emotional voice — terrified style
            ssml_text = f"""<speak version="1.0" 
            xmlns="http://www.w3.org/2001/10/synthesis"
            xmlns:mstts="http://www.w3.org/2001/mstts"
            xml:lang="en-US">
                <voice name="en-US-ChristopherNeural">
                    <mstts:express-as style="terrified" styledegree="1.5">
                        <prosody rate="-15%" pitch="-3Hz">
                            {script}
                        </prosody>
                    </mstts:express-as>
                </voice>
            </speak>"""

            communicate = edge_tts.Communicate(ssml_text, voice_character)
            await communicate.save(str(final_audio_path))

        asyncio.run(save_voice())
        logger.info(f"Natural Male Voice track saved successfully -> {final_audio_path.name}")

    except Exception as e:
        # SSML fail ho toh fallback — normal Edge TTS
        logger.warning(f"SSML failed, falling back to normal Edge TTS: {e}")
        try:
            async def save_voice_fallback():
                communicate = edge_tts.Communicate(
                    script,
                    voice_character,
                    rate="-15%",
                    pitch="-3Hz"
                )
                await communicate.save(str(final_audio_path))

            asyncio.run(save_voice_fallback())
            logger.info(f"Fallback voice saved -> {final_audio_path.name}")

        except Exception as e2:
            logger.error(f"Audio production failed critically: {e2}")
            raise e2

    duration_sec = _get_audio_duration_sec(final_audio_path)

    logger.info("Aligning automated subtitle timing nodes...")
    word_timings = build_word_timings(script, duration_sec)

    timings_path.write_text(json.dumps(word_timings, indent=2), encoding="utf-8")

    return {
        "audio_path":   str(final_audio_path),
        "timings_path": str(timings_path),
        "word_timings": word_timings,
        "duration_sec": duration_sec,
    }


def _get_audio_duration_sec(audio_path: Path) -> float:
    """ffprobe se audio ki exact duration nikalta hai."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ]
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return float(res.stdout.strip())
