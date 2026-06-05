"""
video_compiler.py — Elite Production Compositor Engine (PRODUCTION CORE v10.0 - USA/UK OPTIMIZED)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────

FIXES v10.0 (USA/UK Audience Optimized):
  - Caption position locked to 72% height (safe zone — below UI buttons, above bottom bar)
  - Consistent font: Bold white + black stroke always (no random colors)
  - Keyword highlight: Yellow ONLY for high-impact words (TRAP, DARK, SECRET, etc.)
  - Font size reduced to 72px for readability on mobile screens
  - "Watch till end" hook text added at 3 seconds
  - No more random jumping captions (position was confusing viewers)
"""

import os
import random
import logging
import warnings
import numpy as np
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip
from moviepy.video.fx.all import crop

warnings.filterwarnings("ignore", category=UserWarning, module="moviepy")
logger = logging.getLogger(__name__)

# ─── USA/UK Caption Style Constants ───────────────────────────────────────────
CAPTION_Y_POSITION   = 0.72   # 72% from top = safe zone on all platforms
CAPTION_FONT_SIZE    = 72     # Readable on 5-6" mobile screens
CAPTION_COLOR        = "#FFFFFF"  # Always white base
CAPTION_STROKE_COLOR = "black"
CAPTION_STROKE_WIDTH = 7.0    # Strong outline for readability on any background
CAPTION_HIGHLIGHT_COLOR = "#FFFF00"  # Yellow ONLY for high-impact keywords

# Words that get yellow highlight treatment
HIGHLIGHT_KEYWORDS = {
    "TRAP", "TRAPPED", "DARK", "SECRET", "SECRETS", "CONTROL", "CONTROLS",
    "MANIPULATE", "MANIPULATION", "DOPAMINE", "ADDICTED", "ADDICTION",
    "HACK", "HACKING", "FEAR", "ANXIETY", "DANGEROUS", "DANGER",
    "TRUTH", "EXPOSED", "SHOCKING", "WARNING", "STOP"
}

HOOK_TEXT = "👇 WATCH TILL THE END"
HOOK_DISPLAY_TIME = 3.5   # Show at 3s, disappear after 3.5s duration
HOOK_START_TIME   = 2.8


def apply_dynamic_motion_scale(clip, zoom_ratio=0.06):
    """Applies a smooth continuous zoom transformation matrix safely across frames."""
    def transform_matrix_frame(get_frame, t):
        frame = get_frame(t)
        h, w, c = frame.shape
        scale_factor = 1.0 + (zoom_ratio * t)
        box_h, box_w = int(h / scale_factor), int(w / scale_factor)
        y_offset = (h - box_h) // 2
        x_offset = (w - box_w) // 2
        matrix_crop = frame[y_offset:y_offset+box_h, x_offset:x_offset+box_w]
        from PIL import Image
        pil_img = Image.fromarray(matrix_crop)
        resized_img = pil_img.resize((w, h), Image.Resampling.BICUBIC)
        return np.array(resized_img)
    return clip.fl(transform_matrix_frame)


def apply_text_pop_effect(txt_clip, pop_duration=0.08):
    """Creates a clean kinetic zoom-in pop effect."""
    def text_filter(get_frame, t):
        frame = get_frame(t)
        h, w, c = frame.shape
        scale = 0.70 + (0.30 * (t / pop_duration)) if t < pop_duration else 1.0
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        from PIL import Image
        pil_img = Image.fromarray(frame)
        resized_img = pil_img.resize((new_w, new_h), Image.Resampling.BICUBIC)
        out_frame = np.zeros((h, w, c), dtype=np.uint8)
        pad_x = max(0, (w - new_w) // 2)
        pad_y = max(0, (h - new_h) // 2)
        render_w = min(new_w, w - pad_x)
        render_h = min(new_h, h - pad_y)
        out_frame[pad_y:pad_y+render_h, pad_x:pad_x+render_w] = np.array(resized_img)[0:render_h, 0:render_w]
        return out_frame
    return txt_clip.fl(text_filter)


def get_caption_color(chunk_text: str) -> str:
    """Returns yellow for high-impact keywords, white for everything else."""
    words = set(chunk_text.upper().split())
    if words & HIGHLIGHT_KEYWORDS:
        return CAPTION_HIGHLIGHT_COLOR
    return CAPTION_COLOR


def compile_final_video(video_clips_paths: list, voiceover_data: dict, bgm_file_path: str, output_path: str):
    logger.info("🎬 Initializing USA/UK optimized compositor (v10.0)...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration

    bgm_clip = None
    if bgm_file_path and os.path.exists(bgm_file_path) and os.path.getsize(bgm_file_path) > 20000:
        try:
            bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration).volumex(0.04)
            final_audio = CompositeAudioClip([voice_clip, bgm_clip])
        except:
            final_audio = CompositeAudioClip([voice_clip])
    else:
        final_audio = CompositeAudioClip([voice_clip])

    TARGET_WIDTH  = 1080
    TARGET_HEIGHT = 1920
    processed_clips = []

    clip_slice_duration = max(2.5, (duration / max(1, len(video_clips_paths))) + 0.1)

    for path in video_clips_paths:
        if not path or not os.path.exists(path):
            continue
        try:
            clip = VideoFileClip(path).without_audio().set_duration(clip_slice_duration)
            if clip.w / clip.h < TARGET_WIDTH / TARGET_HEIGHT:
                clip_resized = clip.resize(width=TARGET_WIDTH)
            else:
                clip_resized = clip.resize(height=TARGET_HEIGHT)
            clip_cropped = crop(clip_resized,
                                x_center=clip_resized.w / 2,
                                y_center=clip_resized.h / 2,
                                width=TARGET_WIDTH, height=TARGET_HEIGHT)
            motion_clip = apply_dynamic_motion_scale(clip_cropped, zoom_ratio=0.05)
            processed_clips.append(motion_clip)
        except Exception as ce:
            logger.error(f"⚠️ Discarding faulty clip: {ce}")

    if not processed_clips:
        from moviepy.editor import ColorClip
        processed_clips.append(ColorClip(size=(TARGET_WIDTH, TARGET_HEIGHT),
                                         color=(15, 15, 15)).set_duration(duration))

    base_stitched  = concatenate_videoclips(processed_clips, method="chain")
    stitched_video = base_stitched.set_duration(duration)

    # ── Font setup ────────────────────────────────────────────────────────────
    font_asset_path = "fonts/AmericanCaptain-MdEY.otf"
    if not os.path.exists(font_asset_path):
        font_asset_path = "Impact"

    # ── FIXED caption Y position (pixels from top) ────────────────────────────
    caption_y_px = int(TARGET_HEIGHT * CAPTION_Y_POSITION)   # 1382px

    text_clips = []
    word_timings = voiceover_data["word_timings"]
    chunk_size   = 2   # 2 words per caption chunk = fast, punchy

    for i in range(0, len(word_timings), chunk_size):
        chunk = word_timings[i:i+chunk_size]
        if not chunk or chunk[0]["start"] >= duration:
            continue

        chunk_text = " ".join([item["word"] for item in chunk]).upper()
        start_time = chunk[0]["start"]
        end_time   = min(chunk[-1]["end"], duration)

        if (i + chunk_size) < len(word_timings):
            end_time = min(end_time, word_timings[i + chunk_size]["start"])
        if end_time <= start_time:
            end_time = start_time + 0.35

        # ✅ Color: yellow for power words, white for rest
        text_color = get_caption_color(chunk_text)

        try:
            txt_clip = (TextClip(
                            chunk_text,
                            font=font_asset_path,
                            fontsize=CAPTION_FONT_SIZE,
                            color=text_color,
                            stroke_color=CAPTION_STROKE_COLOR,
                            stroke_width=CAPTION_STROKE_WIDTH,
                            method="caption",
                            size=(TARGET_WIDTH - 160, None),
                            align="center"           # ✅ Always centered
                        )
                        .set_start(start_time)
                        .set_end(end_time))

            animated_txt  = apply_text_pop_effect(txt_clip, pop_duration=0.07)
            # ✅ Fixed position — no more random jumping
            positioned_txt = animated_txt.set_position(("center", caption_y_px))
            text_clips.append(positioned_txt)

        except Exception as text_err:
            logger.error(f"❌ Caption error [{chunk_text}]: {text_err}")

    # ── "Watch till end" hook at 3 seconds ────────────────────────────────────
    hook_end = min(HOOK_START_TIME + HOOK_DISPLAY_TIME, duration)
    if hook_end > HOOK_START_TIME:
        try:
            hook_y_px = int(TARGET_HEIGHT * 0.12)   # Top area, above main captions
            hook_clip = (TextClip(
                             HOOK_TEXT,
                             font=font_asset_path,
                             fontsize=52,
                             color="#FF4444",         # Red — attention grabbing
                             stroke_color="black",
                             stroke_width=5.0,
                             method="caption",
                             size=(TARGET_WIDTH - 160, None),
                             align="center"
                         )
                         .set_start(HOOK_START_TIME)
                         .set_end(hook_end)
                         .set_position(("center", hook_y_px)))
            text_clips.append(hook_clip)
            logger.info(f"✅ Hook text injected at {HOOK_START_TIME}s")
        except Exception as hook_err:
            logger.warning(f"⚠️ Hook text failed: {hook_err}")

    # ── Composite & render ────────────────────────────────────────────────────
    final_composite = CompositeVideoClip(
        [stitched_video] + text_clips,
        size=(TARGET_WIDTH, TARGET_HEIGHT)
    ).set_audio(final_audio)

    logger.info(f"🚀 Rendering optimized output -> {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="7500k",
        threads=4,
        preset="ultrafast",
        logger=None
    )

    final_composite.close()
    stitched_video.close()
    base_stitched.close()
    for c in processed_clips:
        try: c.close()
        except: pass
    voice_clip.close()
    if bgm_clip:
        bgm_clip.close()

    logger.info("✅ USA/UK Optimized Short Compiled Successfully.")
