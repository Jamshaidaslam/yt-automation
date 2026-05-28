"""
video_compiler.py — Core Video Rendering Engine (FIXED NONETYPE GET_FRAME & SPEED OPTIMIZED)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import logging
import textwrap
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoClip,       
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from moviepy.video.fx.all import crop, resize
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

W  = config.VIDEO_WIDTH   # 1080
H  = config.VIDEO_HEIGHT  # 1920
FPS = config.VIDEO_FPS    # 30

FONT_SIZE = 70
CAPTION_TEXT_COLOR = (255, 255, 0, 255)      # Bright Yellow with Full Alpha
CAPTION_STROKE_COLOR = (0, 0, 0, 255)        # Black Outline with Full Alpha

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
    """
    Renders a transparent RGBA PIL image frame, displaying a chunk of 3 words
    synced to the current audio timestamp at the lower third of the screen.
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    active_phrase = ""
    for idx, item in enumerate(word_timings):
        if item["start"] <= t <= item["end"]:
            start_chunk = max(0, idx - (idx % 3))
            end_chunk = min(len(word_timings), start_chunk + 3)
            
            chunk_words = [word_timings[i]["word"].upper() for i in range(start_chunk, end_chunk)]
            active_phrase = " ".join(chunk_words)
            break

    if not active_phrase:
        return np.array(img)

    font = _get_font(FONT_SIZE)
    wrapped_lines = textwrap.wrap(active_phrase, width=18)
    current_y = int(H * 0.75)  # Lower Third Position
    
    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (W - text_w) // 2
        
        for adj_x, adj_y in [(-5,-5), (5,-5), (-5,5), (5,5), (-3,0), (3,0), (0,-3), (0,3)]:
            draw.text((x + adj_x, current_y + adj_y), line, font=font, fill=CAPTION_STROKE_COLOR)
            
        draw.text((x, current_y), line, font=font, fill=CAPTION_TEXT_COLOR)
        current_y += text_h + 20

    return np.array(img)

def compile_video(media_paths: list[str], voiceover_data: dict, output_stem: str) -> str:
    logger.info("Starting video compilation engine...")
    final_path = config.FINAL_VIDEOS_DIR / f"{output_stem}.mp4"
    total_dur  = voiceover_data["duration_sec"]
    word_timings = voiceover_data["word_timings"]

    if not media_paths:
        raise ValueError("Cannot compile video because the list of media paths is empty.")

    video_clips = []
    allocated_raw_clips = [] # 🟢 Keep tracks of all open handles safely
    current_time = 0.0
    media_index = 0

    try:
        MAX_CLIP_DURATION = 2.5

        while current_time < total_dur:
            path_str = media_paths[media_index % len(media_paths)]
            media_index += 1

            clip_path = Path(path_str)
            if not clip_path.exists():
                continue

            raw_clip = VideoFileClip(str(clip_path), audio=False)
            allocated_raw_clips.append(raw_clip) # 🟢 Store here, don't close inside loop!
            
            rem_dur = total_dur - current_time
            clip_duration = min(raw_clip.duration, rem_dur, MAX_CLIP_DURATION)
            
            if clip_duration <= 0.3:
                continue
                
            sub_clip = raw_clip.subclip(0, clip_duration)
            clip_w, clip_h = sub_clip.size
            target_ratio = W / H  
            current_ratio = clip_w / clip_h

            if current_ratio > target_ratio:
                new_w = int(clip_h * target_ratio)
                sub_clip = crop(sub_clip, x_center=clip_w // 2, width=new_w, height=clip_h)
            elif current_ratio < target_ratio:
                new_h = int(clip_w / target_ratio)
                sub_clip = crop(sub_clip, y_center=clip_h // 2, width=clip_w, height=new_h)

            processed_clip = resize(sub_clip, newsize=(W, H))
            video_clips.append(processed_clip)
            
            current_time += clip_duration

        if not video_clips:
            raise RuntimeError("No visual media clips were processed successfully.")

        # Speed Fix: method="compose" bypassing heavy tracking layers
        video_sequence = concatenate_videoclips(video_clips, method="compose")
        
        audio_clip = AudioFileClip(voiceover_data["audio_path"])
        video_sequence = video_sequence.set_audio(audio_clip)

        def make_caption_frame(t):
            frame = _render_caption_frame_cached(t, word_timings)
            return frame[:, :, :3]

        def make_caption_mask(t):
            frame = _render_caption_frame_cached(t, word_timings)
            return frame[:, :, 3] / 255.0

        caption_clip = VideoClip(make_caption_frame, duration=total_dur).set_fps(FPS)
        caption_mask = VideoClip(make_caption_mask, ismask=True, duration=total_dur).set_fps(FPS)
        caption_clip = caption_clip.set_mask(caption_mask)

        final_video = CompositeVideoClip([video_sequence, caption_clip], size=(W, H))
        final_video = final_video.set_duration(total_dur)

        logger.info(f"Rendering compressed fast-cut short output file to -> {final_path}")
        
        # GitHub Cloud Optimized parameters
        final_video.write_videofile(
            str(final_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            bitrate="2500k",          
            audio_bitrate="128k",     
            preset="ultrafast",       
            threads=2,                
            logger=None,
        )

        return str(final_path)

    finally:
        # 🟢 CLEAN UP EVERYTHING AT THE VERY END: No crash, zero memory leak
        for c in video_clips:
            try: c.close()
            except Exception: pass
        for rc in allocated_raw_clips:
            try: rc.close()
            except Exception: pass
        for name in ("video_sequence", "caption_clip", "caption_mask", "final_video", "audio_clip"):
            obj = locals().get(name)
            if obj is not None:
                try: obj.close()
                except Exception: pass
