"""
audio_generator.py — Production Voice Synthesis Layer (v5.3 - STABLE FIXED)
Fixes:
- FileNotFoundError protection
- Async Edge TTS stability
- Safe temp handling
- Production crash prevention
"""

import os
import shutil
import logging
import asyncio
from pathlib import Path

import edge_tts

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════
# CONFIG SAFETY
# ═══════════════════════════════════════

OUTPUT_DIR = Path("output/media")
TEMP_DIR = OUTPUT_DIR / "temp"

VOICE = "en-US-AriaNeural"


def _ensure_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════
# CORE TTS ENGINE
# ═══════════════════════════════════════

async def _generate_tts(text: str, output_path: Path):
    """
    Safe Edge-TTS generator
    """

    communicate = edge_tts.Communicate(text=text, voice=VOICE)

    await communicate.save(str(output_path))


def generate_voiceover(text: str, output_name: str = "voice.mp3") -> str:
    """
    Main safe voice generator (SYNC WRAPPER)
    """

    _ensure_dirs()

    try:
        temp_file = TEMP_DIR / "temp_voice_stream_raw.mp3"
        final_file = OUTPUT_DIR / output_name

        # Run async TTS safely
        asyncio.run(_generate_tts(text, temp_file))

        # Validate file exists
        if not temp_file.exists():
            raise FileNotFoundError(f"TTS failed, file not created: {temp_file}")

        if temp_file.stat().st_size < 1000:
            raise Exception("Generated voice file is too small (failed TTS)")

        # Ensure final dir exists
        final_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy safely
        shutil.copy(temp_file, final_file)

        logger.info(f"✅ Voice generated: {final_file}")

        return str(final_file)

    except Exception as e:
        logger.error(f"❌ Voice generation failed: {e}")
        raise

    finally:
        # cleanup temp file safely
        try:
            if temp_file.exists():
                temp_file.unlink()
        except:
            pass
