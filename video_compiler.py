"""
video_compiler.py — Production Video Compiler (v3.1 - CRASH FIXED)
Fixes:
- voiceover_data string/dict mismatch
- AudioFileClip crash protection
- safe pipeline handling
"""

import os
import logging
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════
# SAFE HELPERS
# ═══════════════════════════════════════

def _resolve_voice_path(voiceover_data):
    """
    FIX: supports BOTH formats:
    - string path
    - dict {"audio_path": "..."}
    """

    if isinstance(voiceover_data, dict):
        path = voiceover_data.get("audio_path")
    else:
        path = voiceover_data

    if not path:
        raise ValueError("❌ Voiceover path missing")

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Voice file not found: {path}")

    return path


def _safe_load_video(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Video clip missing: {path}")
    return VideoFileClip(path)


# ═══════════════════════════════════════
# MAIN COMPILER
# ═══════════════════════════════════════

def compile_final_video(
    video_clips_paths: list,
    voiceover_data,
    bgm_file_path: str,
    output_path: str
):

    logger.info("🎬 Starting video compilation...")

    try:
        # ─────────────────────────────
        # 1. LOAD VIDEO CLIPS
        # ─────────────────────────────
        clips = []

        for path in video_clips_paths:
            try:
                clips.append(_safe_load_video(path))
            except Exception as e:
                logger.warning(f"Skipping clip: {path} | {e}")

        if not clips:
            raise Exception("No valid video clips found")

        final_video = concatenate_videoclips(clips, method="compose")

        # ─────────────────────────────
        # 2. LOAD AUDIO (FIXED)
        # ─────────────────────────────
        voice_path = _resolve_voice_path(voiceover_data)
        voice_clip = AudioFileClip(voice_path)

        final_video = final_video.set_audio(voice_clip)

        # ─────────────────────────────
        # 3. EXPORT VIDEO
        # ─────────────────────────────
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        final_video.write_videofile(
            output_path,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="ultrafast"
        )

        logger.info(f"✅ Video created successfully: {output_path}")

    except Exception as e:
        logger.error(f"❌ Video compilation failed: {e}")
        raise

    finally:
        try:
            final_video.close()
        except:
            pass

        try:
            voice_clip.close()
        except:
            pass

        for c in locals().get("clips", []):
            try:
                c.close()
            except:
                pass
