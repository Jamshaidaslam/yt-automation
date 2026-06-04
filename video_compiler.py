"""
video_compiler.py — Production Compositor Engine (PRODUCTION CORE v5.3 - BUG FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fixes:
  1. font="Impact" hardcoded crash — Linux/CI pe Impact nahi hota, dynamic resolver add kiya
  2. Double .close() bug — stitched_video close pehle, base_stitched baad mein
"""

import os
import logging
from pathlib import Path
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    CompositeAudioClip,
)

import config

logger = logging.getLogger(__name__)


def _resolve_font() -> str:
    """
    FIX: 'Impact' hardcoded tha — GitHub Actions Ubuntu pe yeh font nahi hota.
    Ab pehle custom font try karta hai, phir system fonts, phir default.
    """
    custom_font_path = config.FONTS_DIR / config.FONT_NAME
    if custom_font_path.exists():
        logger.info(f"🔤 Using custom font: {custom_font_path.name}")
        return str(custom_font_path)

    for font_name in ["DejaVu-Sans-Bold", "Liberation-Sans-Bold", "FreeSansBold", "Arial-Bold"]:
        try:
            test = TextClip("test", font=font_name, fontsize=40)
            test.close()
            logger.info(f"🔤 Using system font: {font_name}")
            return font_name
        except Exception:
            continue

    logger.warning("⚠️ No preferred font found. Using MoviePy default.")
    return "DejaVu-Sans"


def compile_final_video(
    video_clips_paths: list,
    voiceover_data: dict,
    bgm_file_path: str,
    output_path: str,
):
    logger.info("🎬 Initializing final audio-visual composite blending layers...")

    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    bgm_clip = None

    if bgm_file_path and os.path.exists(bgm_file_path) and os.path.getsize(bgm_file_path) > 20000:
        try:
            logger.info(f"🎵 Blending background score: {Path(bgm_file_path).name}")
            bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration).volumex(0.05)
            final_audio = CompositeAudioClip([voice_clip, bgm_clip])
        except Exception as audio_err:
            logger.warning(f"⚠️ BGM failed, voice only: {audio_err}")
            final_audio = CompositeAudioClip([voice_clip])
            bgm_clip = None
    else:
        logger.warning("⚠️ No valid BGM. Voice only.")
        final_audio = CompositeAudioClip([voice_clip])

    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920

    logger.info("📐 Compiling and normalizing stock clips...")
    processed_clips = []

    for path in video_clips_paths:
        try:
            clip = VideoFileClip(path).without_audio()
            clip_resized = clip.resize(height=TARGET_HEIGHT)
            w, h = clip_resized.size
            x_center = w // 2
            clip_cropped = clip_resized.crop(
                x1=x_center - (TARGET_WIDTH // 2),
                y1=0,
                x2=x_center + (TARGET_WIDTH // 2),
                y2=TARGET_HEIGHT,
            )
            processed_clips.append(clip_cropped)
        except Exception as clip_err:
            logger.error(f"⚠️ Skipping damaged clip [{path}]: {clip_err}")

    if not processed_clips:
        raise RuntimeError("CRITICAL: Zero usable visual assets. Aborting.")

    base_stitched = concatenate_videoclips(processed_clips, method="compose")
    stitched_video = base_stitched.loop(duration=duration)

    # FIX: font dynamically resolve hoga ab
    font = _resolve_font()
    text_clips = []
    word_timings = voiceover_data["word_timings"]
    chunk_size = 2

    for i in range(0, len(word_timings), chunk_size):
        chunk = word_timings[i: i + chunk_size]
        if not chunk:
            continue

        chunk_text = " ".join([item["word"] for item in chunk]).upper()
        start_time = chunk[0]["start"]
        end_time = chunk[-1]["end"]

        if "WAIT" in chunk_text or "SECRET" in chunk_text:
            text_color = "#FFFF00"
        elif i % 4 == 0:
            text_color = "#00FF00"
        else:
            text_color = "#FFFFFF"

        try:
            txt_clip = (
                TextClip(
                    chunk_text,
                    font=font,
                    fontsize=60,
                    color=text_color,
                    stroke_color="black",
                    stroke_width=4,
                    method="caption",
                    size=(TARGET_WIDTH - 300, None),
                )
                .set_start(start_time)
                .set_end(end_time)
                .set_position(("center", TARGET_HEIGHT * 0.65))
            )
            text_clips.append(txt_clip)
        except Exception as txt_err:
            logger.warning(f"⚠️ TextClip skipped for '{chunk_text}': {txt_err}")

    final_composite = CompositeVideoClip(
        [stitched_video] + text_clips, size=(TARGET_WIDTH, TARGET_HEIGHT)
    ).set_audio(final_audio)

    logger.info(f"🚀 Rendering to: {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
        logger=None,
    )

    # FIX: Correct close order — stitched_video (loop wrapper) pehle close karo,
    # phir base_stitched. Pehle base_stitched close karne se stitched_video corrupt ho sakti thi.
    final_composite.close()
    stitched_video.close()
    base_stitched.close()
    for c in processed_clips:
        c.close()
    voice_clip.close()
    if bgm_clip:
        bgm_clip.close()

    logger.info("✅ Final video compiled successfully!")
