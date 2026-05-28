"""
video_compiler.py — Core Video Rendering Engine (FIXED CONFIG KEYS + NUMPY)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import logging
import math
import os
import textwrap
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoClip,       
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
)
from moviepy.video.fx.all import crop, resize

import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

W  = config.VIDEO_WIDTH   # 1080
H  = config.VIDEO_HEIGHT  # 1920
FPS = config.VIDEO_FPS    # 30

# HARDCODED STYLES FOR CAPTIONS (Safe from config key errors)
FONT_SIZE = 70
CAPTION_TEXT_COLOR = (255, 255, 0)      # High Retention Yellow
CAPTION_STROKE_COLOR = (0, 0, 0)        # Black Border

def _get_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        font_name = getattr(config, "FONT_NAME", None) or getattr(config, "FONT_FILE", "Impact.ttf")
        font_path = config.FONTS_DIR / font_name
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def _render_caption_frame_cached(t: float, word_timings: list[dict]) -> np.ndarray:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    active_word = ""
    for item in word_timings:
        if item["start"] <= t <= item["end"]:
            active_word = item["word"].upper()
            break

    if not active_word:
        return np.array(img.convert("RGB"))

    font = _get_font(FONT_SIZE)
    wrapped_lines = textwrap.wrap(active_word, width=12)
    current_y = H // 2 - (len(wrapped_lines) * FONT_SIZE) // 2
    
    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (W - text_w) // 2
        
        for adj_x, adj_y in [(-4,-4), (4,-4), (-4,4), (4,4), (-2,0), (2,0), (0,-2), (0,2)]:
            draw.text((x + adj_x, current_y + adj_y), line, font=font, fill=CAPTION_STROKE_COLOR)
            
        draw.text((x, current_y), line, font=font, fill=CAPTION_TEXT_COLOR)
        current_y += text_h + 20

    return np.array(img.convert("RGB"))

def _build_caption_clip(word_timings: list[dict], total_duration: float):
    def make_frame(t):
        return _render_caption_frame_cached(t, word_timings)

    clip = VideoClip(make_frame, duration=total_duration)
    return clip.set_fps(FPS)

def compile_video(media_paths: list[str], voiceover_data: dict, output_stem: str) -> str:
    logger.info("Starting video compilation engine...")
    final_path = config.FINAL_VIDEOS_DIR / f"{output_stem}.mp4"
    total_dur  = voiceover_data["duration_sec"]
    word_timings = voiceover_data["word_timings"]

    if not media_paths:
        raise ValueError("Cannot compile video because the list of media paths is empty.")

    video_clips = []
    current_time = 0.0

    try:
        for path_str in media_paths:
            if current_time >= total_dur:
                break

            clip_path = Path(path_str)
            if not clip_path.exists():
                continue

            clip = VideoFileClip(str(clip_path), audio=False)
            rem_dur = total_dur - current_time
            clip_duration = min(clip.duration, rem_dur)
            
            if clip_duration <= 0.5:
                clip.close()
                continue
                
            clip = clip.subclip(0, clip_duration)
            clip_w, clip_h = clip.size
            target_ratio = W / H  
            current_ratio = clip_w / clip_h

            if current_ratio > target_ratio:
                new_w = int(clip_h * target_ratio)
                clip = crop(clip, x_center=clip_w // 2, width=new_w, height=clip_h)
            elif current_ratio < target_ratio:
                new_h = int(clip_w / target_ratio)
                clip = crop(clip, y_center=clip_h // 2, width=clip_w, height=new_h)

            clip = resize(clip, newsize=(W, H))
            video_clips.append(clip)
            current_time += clip_duration

        if not video_clips:
            raise RuntimeError("No visual media clips were processed successfully.")

        video_sequence = concatenate_videoclips(video_clips, method="compose")
        audio_clip = AudioFileClip(voiceover_data["audio_path"])
        video_sequence = video_sequence.set_audio(audio_clip)

        caption_clip = _build_caption_clip(word_timings, total_dur)

        final_video = CompositeVideoClip([video_sequence, caption_clip], size=(W, H))
        final_video = final_video.set_duration(total_dur)

        logger.info(f"Rendering final short output file to -> {final_path}")
        final_video.write_videofile(
            str(final_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",  
            threads=4,
            logger=None,
        )

        return str(final_path)

    finally:
        for c in video_clips:
            try: c.close()
            except Exception: pass
        for name in ("video_sequence", "caption_clip", "final_video", "audio_clip"):
            obj = locals().get(name)
            if obj is not None:
                try: obj.close()
                except Exception: pass
