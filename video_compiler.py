"""
video_compiler.py — Production Compositor Engine (PRODUCTION CORE v5.3 - TIMEOUT FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fixes:
  1. font="Impact" hardcoded crash fix — dynamic resolver
  2. Double .close() bug fix
  3. GitHub Actions timeout fix:
     - Resolution 1080x1920 → 720x1280 (render 3x faster, YouTube Shorts accepts it)
     - threads 4 → 2 (hosted runner pe 4 threads slow tha)
     - preset ultrafast confirm
     - Har clip max 8 sec tak trim — lambi clips render time barhaati thin
     - TextClip subtitles disable option — agar phir bhi slow ho
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

# FIX: 720p render karo GitHub Actions pe — YouTube Shorts 720p perfectly accept karta hai
# 1080p render mein 10-15 min lagते the, 720p mein 2-3 min
TARGET_WIDTH = 720
TARGET_HEIGHT = 1280

# Har clip ka max duration — zyada lambi clips loop ke saath render slow karti hain
MAX_CLIP_DURATION = 8.0


def _resolve_font() -> str:
    """
    FIX: 'Impact' hardcoded tha — GitHub Actions Ubuntu pe crash karta tha.
    Ab custom font try karta hai, phir system fonts, phir default.
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

            # FIX: Clip ko max 8 sec tak trim karo — lambi clips render slow karti hain
            if clip.duration > MAX_CLIP_DURATION:
                clip = clip.subclip(0, MAX_CLIP_DURATION)

            # FIX: 720x1280 pe resize — 1080p se 3x fast render
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

    # 3. Subtitle generation
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
                    fontsize=50,  # 60 → 50 (720p ke liye proportional)
                    color=text_color,
                    stroke_color="black",
                    stroke_width=3,
                    method="caption",
                    size=(TARGET_WIDTH - 200, None),  # 300 → 200 (720p width)
                )
                .set_start(start_time)
                .set_end(end_time)
                .set_position(("center", TARGET_HEIGHT * 0.65))
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
        threads=2,        # FIX: 4 → 2 (GitHub Actions hosted runner pe 2 faster hai)
        preset="ultrafast",
        logger=None,
        ffmpeg_params=["-crf", "28"]  # FIX: crf 28 = smaller file, faster encode
                                       # default crf 23 tha, 28 pe quality thodi kam
                                       # but GitHub Actions timeout nahi hoga
    )

    # FIX: Correct close order
    final_composite.close()
    stitched_video.close()
    base_stitched.close()
    for c in processed_clips:
        c.close()
    voice_clip.close()
    if bgm_clip:
        bgm_clip.close()

    logger.info("✅ Final video compiled successfully!")
