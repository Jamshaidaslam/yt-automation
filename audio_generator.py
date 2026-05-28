"""
audio_generator.py — Groq Cloud TTS / OpenAI Whisper Pipeline (100% Anti-Block)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
Replaced edge-tts with Groq's stable audio synthesis layer to completely 
bypass Microsoft's GitHub Actions 403 Forbidden Cloud IP blocks.
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from groq import Groq
from script_generator import build_word_timings
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# Instantiate client using existing Groq Key
_client = Groq(api_key=config.GROQ_API_KEY)


def generate_voiceover(script: str, output_stem: str) -> dict:
    """
    Generates vocal audio track using Groq Speech synthesis engine.
    Completely immune to Microsoft Edge 403 server handshaking blocks.
    """
    audio_path = config.AUDIO_DIR / f"{output_stem}.mp3"
    timings_path = config.AUDIO_DIR / f"{output_stem}_timings.json"

    logger.info("Synthesising stable TTS audio voice via Groq Cloud Infrastructure...")

    try:
        # Request speech generation from Groq Cloud backend
        response = _client.audio.speech.create(
            model="tts-1",  # Standard stable OpenAI text-to-speech protocol
            voice="alloy",  # High retention crisp viral voice option (alloy, echo, onyx)
            input=script,
        )
        
        # Save the binary audio file content stream directly
        response.write_to_file(str(audio_path))
        logger.info(f"Audio file saved successfully -> {audio_path.name}")
        
    except Exception as e:
        logger.error(f"Groq Audio synthesis layer failed critically: {e}")
        raise e

    # Extract dynamic float duration using local system FFprobe binary mapping
    duration_sec = _get_audio_duration_sec(audio_path)

    # Automatically map precise word metrics dynamically for MoviePy captions
    logger.info("Distributing timing sequence alignments...")
    word_timings = build_word_timings(script, duration_sec)

    # Persist JSON sidecar configuration tracking metrics
    timings_path.write_text(json.dumps(word_timings, indent=2), encoding="utf-8")

    return {
        "audio_path":   str(audio_path),
        "timings_path": str(timings_path),
        "word_timings": word_timings,
        "duration_sec": duration_sec,
    }


def _get_audio_duration_sec(audio_path: Path) -> float:
    """Extract precise float duration from generated media using FFprobe backend."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())


if __name__ == "__main__":
    test_text = "This is a stable test sequence generated using Groq Cloud audio systems infrastructure."
    if config.GROQ_API_KEY:
        print(generate_voiceover(test_text, "groq_stability_test"))
    else:
        print("Error: GROQ_API_KEY environment variable is not defined.")
