"""
video_compiler.py — Production Video Compiler (v4.0 - ALL BUGS FIXED)
Fixes:
- NameError: final_video/voice_clip undefined in finally block
- BGM mixing actually implemented (was accepted but never used)
- clips list unavailable in finally via locals() — fixed with explicit tracking
- voiceover_data string/dict mismatch (kept from v3.1)
- AudioFileClip crash protection (kept from v3.1)
"""

import os
import logging
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════
# SAFE HELPERS
# ═══════════════════════════════════════

def _resolve_voice_path(voiceover_data):
    """
    Supports BOTH formats:
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
    output_path: str,
    bgm_volume: float = 0.08,   # BGM ki volume — 0.0 to 1.0
):
    logger.info("🎬 Starting video compilation...")

    # FIX: finally mein NameError se bachne ke liye
    # saare resources pehle None set karo
    clips = []
    final_video = None
    voice_clip = None
    bgm_clip = None

    try:
        # ─────────────────────────────
        # 1. LOAD VIDEO CLIPS
        # ─────────────────────────────
        for path in video_clips_paths:
            try:
                clips.append(_safe_load_video(path))
            except Exception as e:
                logger.warning(f"Skipping clip: {path} | {e}")

        if not clips:
            raise Exception("No valid video clips found")

        final_video = concatenate_videoclips(clips, method="compose")

        # ─────────────────────────────
        # 2. LOAD VOICEOVER
        # ─────────────────────────────
        voice_path = _resolve_voice_path(voiceover_data)
        voice_clip = AudioFileClip(voice_path)

        # ─────────────────────────────
        # 3. BGM MIXING (FIXED — ab actually kaam karta hai)
        # ─────────────────────────────
        if bgm_file_path and os.path.exists(bgm_file_path):
            try:
                bgm_clip = (
                    AudioFileClip(bgm_file_path)
                    .volumex(bgm_volume)                    # volume kam karo
                    .subclip(0, final_video.duration)       # video ki length tak trim karo
                )
                # Voice + BGM mix karo
                mixed_audio = CompositeAudioClip([voice_clip, bgm_clip])
                final_video = final_video.set_audio(mixed_audio)
                logger.info(f"🎵 BGM mixed at volume {bgm_volume}: {bgm_file_path}")
            except Exception as e:
                # BGM fail ho toh sirf voice use karo — crash mat karo
                logger.warning(f"⚠️ BGM mixing failed, using voice only: {e}")
                final_video = final_video.set_audio(voice_clip)
        else:
            if bgm_file_path:
                logger.warning(f"⚠️ BGM file not found, skipping: {bgm_file_path}")
            final_video = final_video.set_audio(voice_clip)

        # ─────────────────────────────
        # 4. EXPORT VIDEO
        # ─────────────────────────────
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        final_video.write_videofile(
            output_path,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="ultrafast",
        )

        logger.info(f"✅ Video created successfully: {output_path}")

    except Exception as e:
        logger.error(f"❌ Video compilation failed: {e}")
        raise

    finally:
        # FIX: None check ke saath close karo — NameError nahi aayega
        if final_video is not None:
            try:
                final_video.close()
            except Exception:
                pass

        if voice_clip is not None:
            try:
                voice_clip.close()
            except Exception:
                pass

        if bgm_clip is not None:
            try:
                bgm_clip.close()
            except Exception:
                pass

        for c in clips:
            try:
                c.close()
            except Exception:
                pass
