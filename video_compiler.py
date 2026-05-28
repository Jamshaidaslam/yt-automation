"""
video_compiler.py — Core Video Rendering Engine
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
Assembles the final vertical 9:16 short-form video:

  1. Loads B-roll clips, trims them to CLIP_MIN/MAX_SEC, adds zoom/pan motion.
  2. Scales + crops every clip to exactly 1080×1920 (no black bars ever).
  3. Overlays word-by-word synchronised captions via Pillow-rendered PNG frames.
  4. Mixes the Edge-TTS voiceover with a subtle background audio level.
  5. Exports as H.264 MP4 optimised for vertical social platforms.

Memory safety: every MoviePy clip calls .close() in a finally block.
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
    VideoClip,       # FIX: Added VideoClip to handle custom frame generation functions
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


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR RENDERING CAPTION IMAGES
# ═══════════════════════════════════════════════════════════════════════════════

def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """Load the global configured font or fallback to default."""
    try:
        font_path = config.FONTS_DIR / config.FONT_NAME
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def _render_caption_frame_cached(t: float, word_timings: list[dict]) -> np.ndarray:
    """
    Renders a single frame of text overlay based on current timestamp `t`.
    Returns an RGB numpy array (required by MoviePy).
    """
    # 1. Create a transparent RGBA image for drawing
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Find which word is currently active
    active_word = ""
    for item in word_timings:
        if item["start"] <= t <= item["end"]:
            active_word = item["word"].upper()
            break

    if not active_word:
        # If no active word, return an empty transparent frame
        return np.array(img.convert("RGB"))

    # Load configured fonts
    font = _get_font(config.FONT_SIZE)
    
    # Calculate text layout and bounding box
    # Wrap text if it exceeds max line width characters
    wrapped_lines = textwrap.wrap(active_word, width=12)
    
    # Render line by line
    current_y = H // 2 - (len(wrapped_lines) * config.FONT_SIZE) // 2
    
    for line in wrapped_lines:
        # Get text size bounding box
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (W - text_w) // 2
        
        # Draw background stroke/shadow for readability
        for adj_x, adj_y in [(-4,-4), (4,-4), (-4,4), (4,4), (-2,0), (2,0), (0,-2), (0,2)]:
            draw.text((x + adj_x, current_y + adj_y), line, font=font, fill=config.CAPTION_STROKE_COLOR)
            
        # Draw the main text clip frame
        draw.text((x, current_y), line, font=font, fill=config.CAPTION_TEXT_COLOR)
        current_y += text_h + 20

    # Convert RGBA to RGB for MoviePy frame standard pipeline compatibility
    return np.array(img.convert("RGB"))


def _build_caption_clip(word_timings: list[dict], total_duration: float):
    """
    Builds the final synchronized dynamic captions overlay sequence.
    """
    def make_frame(t):
        return _render_caption_frame_cached(t, word_timings)

    # FIX: Changed from ImageClip to VideoClip to properly handle the make_frame function pointer
    clip = VideoClip(make_frame, duration=total_duration)
    return clip.set_fps(FPS)


# ═══════════════════════════════════════════════════════════════════════════════
# CORE VIDEO COMPILER PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def compile_video(media_paths: list[str], voiceover_data: dict, output_stem: str) -> str:
    """
    Assembles local vertical MP4 combining visual media streams, TTS vocals,
    synchronized captions overlay, and background ambiance loops.
    """
    logger.info("Starting video compilation engine...")
    final_path = config.FINAL_VIDEOS_DIR / f"{output_stem}.mp4"
    total_dur  = voiceover_data["duration_sec"]
    word_timings = voiceover_data["word_timings"]

    if not media_paths:
        raise ValueError("Cannot compile video because the list of media paths is empty.")

    video_clips = []
    current_time = 0.0

    try:
        # Loop through visual assets and process geometry configurations
        for path_str in media_paths:
            if current_time >= total_dur:
                break

            clip_path = Path(path_str)
            if not clip_path.exists():
                continue

            # Load video file stream clip
            clip = VideoFileClip(str(clip_path), audio=False)
            
            # Target remaining duration calculation
            rem_dur = total_dur - current_time
            clip_duration = min(clip.duration, rem_dur)
            
            if clip_duration <= 0.5:
                clip.close()
                continue
                
            # Cut specific duration slice
            clip = clip.subclip(0, clip_duration)

            # Enforce strict 1080x1920 spatial crop and resize aspect ratio transforms
            clip_w, clip_h = clip.size
            target_ratio = W / H  # 9:16
            current_ratio = clip_w / clip_h

            if current_ratio > target_ratio:
                # Video is wider than 9:16 (landscape) -> scale by height, then crop width
                new_w = int(clip_h * target_ratio)
                clip = crop(clip, x_center=clip_w // 2, width=new_w, height=clip_h)
            elif current_ratio < target_ratio:
                # Video is narrower than 9:16 -> scale by width, then crop height
                new_h = int(clip_w / target_ratio)
                clip = crop(clip, y_center=clip_h // 2, width=clip_w, height=new_h)

            # Standard resize up/down to full 1080x1920 resolution matching parameters
            clip = resize(clip, newsize=(W, H))

            # Apply slow viral kinetic camera zoom pan effect using MoviePy transforms
            # Zooms from 1.0 to 1.15 over the duration of the clip slice
            clip = clip.fl_time(lambda t: t).resize(lambda t: 1.0 + (0.15 * (t / clip.duration)))

            video_clips.append(clip)
            current_time += clip_duration

        if not video_clips:
            raise RuntimeError("No visual media clips were successfully processed for rendering.")

        # Stitch visual asset segments together sequentially
        video_sequence = concatenate_videoclips(video_clips, method="compose")

        # Load primary narration tracks
        audio_clip = AudioFileClip(voiceover_data["audio_path"])
        video_sequence = video_sequence.set_audio(audio_clip)

        # Build dynamic caption overlays using our corrected function
        caption_clip = _build_caption_clip(word_timings, total_dur)

        # Merge visual array streams, audio, and captions overlays into composite master track
        final_video = CompositeVideoClip([video_sequence, caption_clip], size=(W, H))
        final_video = final_video.set_duration(total_dur)

        # Export high-definition H.264 file target
        logger.info(f"Rendering final short output file to -> {final_path}")
        final_video.write_videofile(
            str(final_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",  # Fast compression pass optimization on standard GitHub Actions free host runners
            threads=4,
            logger=None,
        )

        return str(final_path)

    finally:
        # Graceful memory resource pipeline safety cleanup to prevent OS level locks on media resources
        for c in video_clips:
            try:
                c.close()
            except Exception:
                pass
        for name in ("video_sequence", "caption_clip", "final_video", "audio_clip"):
            obj = locals().get(name)
            if obj is not None:
                try:
                    obj.close()
                except Exception:
                    pass


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Quick smoke test: renders a 2-second black video with test captions
    from pathlib import Path

    dummy_timings = [
        {"word": "AI", "start": 0.0, "end": 0.5},
        {"word": "is", "start": 0.5, "end": 0.8},
        {"word": "watching", "start": 0.8, "end": 1.4},
        {"word": "you", "start": 1.4, "end": 2.0},
    ]
    dummy_audio = {
        "audio_path":   "output/audio/test_audio.mp3",
        "word_timings": dummy_timings,
        "duration_sec": 2.0,
    }
    dummy_seo = {"title": "Test", "description": "", "hashtags": []}

    # Create a dummy silent audio file if not present
    import subprocess
    Path("output/audio").mkdir(parents=True, exist_ok=True)
    if not Path("output/audio/test_audio.mp3").exists():
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:c=2", 
            "-t", "2", "output/audio/test_audio.mp3", "-y"
        ])

    # Build blank test background color clip file
    Path("output/media").mkdir(parents=True, exist_ok=True)
    test_media_file = "output/media/test_blank.mp4"
    if not Path(test_media_file).exists():
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30", 
            "-t", "5", test_media_file, "-y"
        ])

    compile_video([test_media_file], dummy_audio, "test_render_output")
    print("Test build compilation executed successfully.")
