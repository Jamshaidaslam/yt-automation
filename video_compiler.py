"""
video_compiler.py — Production Compositor Engine (PRODUCTION CORE v5.5 - DYNAMIC CAPTIONS FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fixes & Upgrades:
  1. Kinetic Screen-Bouncing Captions Engine Added (UP-GREEN -> DOWN-BLUE -> CENTER-YELLOW)
  2. 3-Words per Chunk Dynamic Sentence Formula Lock
  3. Smooth Zoom-In Kinetic Animation Function (.fx resize)
  4. GitHub Actions Environment Performance Optimized (720p Layout)
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
import moviepy.video.fx.all as vfx

import config

logger = logging.getLogger(__name__)

# GitHub Actions optimization -> 720p accepts perfectly for Shorts/Reels
TARGET_WIDTH = 720
TARGET_HEIGHT = 1280
MAX_CLIP_DURATION = 8.0


def _resolve_font() -> str:
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

    # 1. Audio setup
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    logger.info(f"🎙️ Voiceover duration: {round(duration, 2)}s")
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

    # 2. Process B-roll clips
    logger.info(f"📐 Compiling clips at {TARGET_WIDTH}x{TARGET_HEIGHT}...")
    processed_clips = []

    for path in video_clips_paths:
        try:
            clip = VideoFileClip(path).without_audio()

            if clip.duration > MAX_CLIP_DURATION:
                clip = clip.subclip(0, MAX_CLIP_DURATION)

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
            logger.info(f"✅ Clip loaded: {Path(path).name}")
        except Exception as clip_err:
            logger.error(f"⚠️ Skipping damaged clip [{path}]: {clip_err}")

    if not processed_clips:
        raise RuntimeError("CRITICAL: Zero usable visual assets. Aborting.")

    base_stitched = concatenate_videoclips(processed_clips, method="compose")
    stitched_video = base_stitched.loop(duration=duration)

    # 3. 🔥 UPGRADE: Kinetic Screen-Bouncing Subtitle Generation Logic
    font = _resolve_font()
    text_clips = []
    word_timings = voiceover_data["word_timings"]
    
    # 3 words ka elite chunk formula lock kia ha
    chunk_size = 3

    for i in range(0, len(word_timings), chunk_size):
        chunk = word_timings[i: i + chunk_size]
        if not chunk:
            continue

        chunk_text = " ".join([item["word"] for item in chunk]).upper()
        start_time = chunk[0]["start"]
        end_time = chunk[-1]["end"]
        clip_duration = end_time - start_time
        
        if clip_duration <= 0:
            clip_duration = 0.1  # Safety fallback boundary

        # Dynamic Loop Counter for Screen Positions
        loop_index = (i // chunk_size) % 3

        if loop_index == 0:
            # 🟢 UP POSITION (Neon Green Style)
            pos_y = int(TARGET_HEIGHT * 0.18)
            text_color = "#00FF00"
            font_size = 65  # 720p screen size ke mutabiq scaled down from 85
        elif loop_index == 1:
            # 🔵 DOWN POSITION (Electric Cyan Blue Style)
            pos_y = int(TARGET_HEIGHT * 0.78)
            text_color = "#00FFFF"
            font_size = 60
        else:
            # 🟡 CENTER POSITION (Bright Yellow Accent Style)
            pos_y = int(TARGET_HEIGHT * 0.45)
            text_color = "#FFFF00"
            font_size = 70

        # Special keywords detection trigger to lock focus
        if "WAIT" in chunk_text or "SECRET" in chunk_text or "HACKED" in chunk_text:
            text_color = "#FF3333"  # Crimson Red for high danger thrill triggers
            font_size = int(font_size * 1.15)

        try:
            # Define standard pop zoom interpolation curve
            def dynamic_zoom_pop(t):
                pop_speed = 0.15  # 0.15 seconds me animation deploy ho jayegi
                if t < pop_speed:
                    return 0.75 + (0.25 * (t / pop_speed))  # 75% se 100% smoothly popup karega
                return 1.0

            txt_clip = (
                TextClip(
                    chunk_text,
                    font=font,
                    fontsize=font_size,
                    color=text_color,
                    stroke_color="black",
                    stroke_width=5,  # Strong heavy outline for high-retention readability
                    method="caption",
                    size=(TARGET_WIDTH - 120, None),
                )
                .set_start(start_time)
                .set_end(end_time)
                .set_duration(clip_duration)
                .fx(vfx.resize, dynamic_zoom_pop)  # 🔥 Dynamic Zoom Activation Frame Hook
                .set_position(("center", pos_y))
            )
            text_clips.append(txt_clip)
        except Exception as txt_err:
            logger.warning(f"⚠️ TextClip skipped for '{chunk_text}': {txt_err}")

    # 4. Composite and render
    final_composite = CompositeVideoClip(
        [stitched_video] + text_clips, size=(TARGET_WIDTH, TARGET_HEIGHT)
    ).set_audio(final_audio)

    logger.info(f"🚀 Rendering to: {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=2,
        preset="ultrafast",
        logger=None,
        ffmpeg_params=["-crf", "28"]
    )

    # Correct close cleanup sequence
    final_composite.close()
    stitched_video.close()
    base_stitched.close()
    for c in processed_clips:
        c.close()
    voice_clip.close()
    if bgm_clip:
        bgm_clip.close()

    logger.info("✅ Final video compiled successfully with Screen-Bouncing Kinetic Captions!")
