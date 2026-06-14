"""
audio_generator.py — Production Voice Synthesis Layer (v5.4 - FULL STABLE FIX)
Fixes:
- TypeError: voice_type support added
- FileNotFoundError protection
- Async Edge-TTS crash fix
- Safe temp + cleanup handling
- Production-ready CI stability
"""

import os
import shutil
import logging
import asyncio
from pathlib import Path

import edge_tts

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════

OUTPUT_DIR = Path("output/media")
TEMP_DIR = OUTPUT_DIR / "temp"

DEFAULT_VOICE = "en-US-AriaNeural"

VOICE_MAP = {
    "male": "en-US-GuyNeural",
    "female": "en-US-AriaNeural",
    "neutral": "en-US-JennyNeural"
}


# ═══════════════════════════════════════
# SAFETY UTIL
# ═══════════════════════════════════════

def _ensure_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def _validate_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"TTS file not created: {path}")

    if path.stat().st_size < 1000:
        raise Exception(f"TTS file too small (likely failed): {path}")


# ═══════════════════════════════════════
# CORE TTS ENGINE
# ═══════════════════════════════════════

async def _generate_tts(text: str, voice: str, output_path: Path):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(str(output_path))


# ═══════════════════════════════════════
# MAIN FUNCTION (FIXED + BACKWARD COMPATIBLE)
# ═══════════════════════════════════════

def generate_voiceover(
    text: str,
    output_name: str = "voice.mp3",
    voice_type: str = "female"
) -> str:
    """
    Generate voiceover using Edge-TTS (SAFE VERSION)

    Supports:
    - voice_type: male / female / neutral
    - backward compatible calls
    """

    _ensure_dirs()

    voice = VOICE_MAP.get(voice_type, DEFAULT_VOICE)

    temp_file = TEMP_DIR / "temp_voice_stream_raw.mp3"
    final_file = OUTPUT_DIR / output_name

    try:
        # 🧠 Generate TTS (async safe run)
        asyncio.run(_generate_tts(text, voice, temp_file))

        # 🔍 Validate output
        _validate_file(temp_file)

        # 📁 Ensure output directory exists
        final_file.parent.mkdir(parents=True, exist_ok=True)

        # 📦 Move file safely
        shutil.copy(temp_file, final_file)

        logger.info(f"✅ Voice generated successfully: {final_file}")

        return str(final_file)

    except Exception as e:
        logger.error(f"❌ Voice generation failed: {e}")
        raise

    finally:
        # 🧹 Cleanup temp file safely
        try:
            if temp_file.exists():
                temp_file.unlink()
        except Exception:
            pass
