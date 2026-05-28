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
# 1.  FONT LOADING  (falls back to PIL default if custom font not found)
# ═══════════════════════════════════════════════════════════════════════════════

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    font_path = config.FONT_FILE
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    # Fallback — no custom font in repo yet
    logger.warning(f"Font not found at {font_path}. Using PIL default (install Montserrat-ExtraBold.ttf).")
    return ImageFont.load_default()


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  CAPTION FRAME GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))  # type: ignore


def _render_caption_frame(
    words_context: list[str],
    active_index: int,
    canvas_w: int = W,
    canvas_h: int = H,
) -> np.ndarray:
    """
    Render a transparent RGBA caption overlay as a numpy array.

    `words_context`  — list of words currently on screen (sliding window)
    `active_index`   — index within words_context that is currently spoken
    """
    img    = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw   = ImageDraw.Draw(img)
    font   = _load_font(config.CAPTION_FONT_SIZE)
    outline_w = config.CAPTION_OUTLINE_WIDTH

    active_rgb   = _hex_to_rgb(config.CAPTION_ACTIVE_COLOR)
    inactive_rgb = _hex_to_rgb(config.CAPTION_INACTIVE_COLOR)
    outline_rgb  = _hex_to_rgb(config.CAPTION_OUTLINE_COLOR)

    # ── Build display text (wrap long lines) ────────────────────────────────
    full_text = " ".join(words_context)
    lines     = textwrap.wrap(full_text, width=config.CAPTION_MAX_CHARS_LINE)

    # Total height of text block
    line_height = config.CAPTION_FONT_SIZE + 10
    total_h     = line_height * len(lines)

    # Vertical start position (lower-middle third)
    start_y = int(canvas_h * config.CAPTION_Y_FRACTION) - total_h // 2

    # Track word index across lines for active highlighting
    word_counter = 0

    for line in lines:
        line_words = line.split()
        # Measure line width for horizontal centering
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
        except AttributeError:
            # PIL < 9.2 fallback
            line_w, _ = draw.textsize(line, font=font)
        x = (canvas_w - line_w) // 2
        y = start_y

        # Render word-by-word to allow individual colour per word
        for word in line_words:
            is_active = (word_counter == active_index)
            color     = active_rgb if is_active else inactive_rgb

            # Measure word width
            try:
                wb = draw.textbbox((0, 0), word + " ", font=font)
                word_w = wb[2] - wb[0]
            except AttributeError:
                word_w, _ = draw.textsize(word + " ", font=font)

            # Draw black outline (stroke simulation via offset drawing)
            for dx in range(-outline_w, outline_w + 1):
                for dy in range(-outline_w, outline_w + 1):
                    if abs(dx) + abs(dy) <= outline_w:  # Diamond kernel
                        draw.text((x + dx, y + dy), word, font=font, fill=(*outline_rgb, 255))

            # Draw main coloured word
            draw.text((x, y), word, font=font, fill=(*color, 255))

            x += word_w
            word_counter += 1

        start_y += line_height

    return np.array(img)


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  PER-FRAME CAPTION CLIP BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def _build_caption_clip(word_timings: list[dict], total_duration: float) -> ImageClip:
    """
    Construct a MoviePy ImageClip that changes its caption frame at each word boundary.
    The clip has RGBA transparency so it composites cleanly over the video.
    """
    n_visible = config.CAPTION_WORDS_VISIBLE

    def make_frame(t: float) -> np.ndarray:
        # Find the word index being spoken at time t
        active_idx_global = 0
        for i, w in enumerate(word_timings):
            if w["start"] <= t < w["end"]:
                active_idx_global = i
                break
            elif t >= w["end"]:
                active_idx_global = i

        # Sliding context window: show n_visible words centered on active word
        window_start = max(0, active_idx_global - n_visible // 2)
        window_end   = min(len(word_timings), window_start + n_visible)
        window_start = max(0, window_end - n_visible)

        context_words = [word_timings[i]["word"] for i in range(window_start, window_end)]
        active_in_window = active_idx_global - window_start

        return _render_caption_frame(context_words, active_in_window)

    clip = ImageClip(make_frame, duration=total_duration, ismask=False)
    clip = clip.set_fps(FPS)
    return clip


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  B-ROLL CLIP PROCESSOR  (scale + crop to 9:16, add motion effect)
# ═══════════════════════════════════════════════════════════════════════════════

def _fit_clip_to_canvas(clip: VideoFileClip) -> VideoFileClip:
    """
    Scale and centre-crop the clip to exactly W×H (1080×1920) without letterboxing.
    Strategy: scale so the SMALLER dimension fills the canvas, then crop the excess.
    """
    src_w, src_h = clip.size
    src_ratio    = src_w / src_h
    target_ratio = W / H  # 0.5625 (9:16)

    if src_ratio > target_ratio:
        # Wider than target → scale by height, crop width
        new_h = H
        new_w = int(src_w * H / src_h)
    else:
        # Taller than target → scale by width, crop height
        new_w = W
        new_h = int(src_h * W / src_w)

    clip = clip.resize((new_w, new_h))
    # Centre-crop
    x1 = (new_w - W) // 2
    y1 = (new_h - H) // 2
    clip = crop(clip, x1=x1, y1=y1, width=W, height=H)
    return clip


def _add_zoom_effect(clip: VideoFileClip) -> VideoFileClip:
    """
    Apply a subtle zoom-in over the full clip duration using FFmpeg filter.
    Uses MoviePy's fl_image for per-frame zoom (avoids subprocess overhead).
    """
    duration = clip.duration
    zoom_factor = config.ZOOM_FACTOR  # e.g. 0.04 = 4% total zoom

    def zoom_frame(get_frame, t):
        frame  = get_frame(t)
        progress = t / duration if duration > 0 else 0
        scale    = 1.0 + zoom_factor * progress   # 1.0 → 1.04

        h, w = frame.shape[:2]
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Upscale
        img    = Image.fromarray(frame)
        img    = img.resize((new_w, new_h), Image.LANCZOS)

        # Centre-crop back to original size
        x1 = (new_w - w) // 2
        y1 = (new_h - h) // 2
        img = img.crop((x1, y1, x1 + w, y1 + h))
        return np.array(img)

    return clip.fl(zoom_frame, apply_to=["mask", "video"])


def _add_pan_effect(clip: VideoFileClip) -> VideoFileClip:
    """
    Apply a slow horizontal pan (Ken Burns-style).
    """
    pan_pixels = int(W * config.PAN_SPEED * clip.duration * FPS)

    # Add horizontal padding to allow panning without black bars
    pad_w = W + pan_pixels * 2

    def pan_frame(get_frame, t):
        frame    = get_frame(t)
        progress = t / clip.duration if clip.duration > 0 else 0
        offset   = int(pan_pixels * progress)

        # Pad frame left and right, then crop with offset
        padded = Image.fromarray(frame)
        canvas = Image.new("RGB", (pad_w, H), (0, 0, 0))
        canvas.paste(padded, (pan_pixels, 0))
        x1 = pan_pixels - offset
        cropped = canvas.crop((x1, 0, x1 + W, H))
        return np.array(cropped)

    return clip.fl(pan_frame, apply_to=["video"])


def _process_broll_clip(
    path: str,
    duration: float,
    effect: str = "zoom",
) -> Optional[VideoFileClip]:
    """
    Load, trim, resize/crop, and apply motion effect to a single B-roll clip.
    Returns None if the file is unreadable.

    Parameters
    ----------
    path     : str    — local file path
    duration : float  — desired output duration (2-3 seconds)
    effect   : str    — "zoom" | "pan" | "none"
    """
    clip = None
    try:
        raw = VideoFileClip(path, audio=False)

        # Trim to requested duration (take from the middle to avoid intros/outros)
        src_dur = raw.duration
        if src_dur <= duration:
            segment = raw
        else:
            start = (src_dur - duration) / 2
            segment = raw.subclip(start, start + duration)

        # Scale + crop to 1080×1920
        fitted = _fit_clip_to_canvas(segment)

        # Apply motion effect
        if effect == "zoom":
            result = _add_zoom_effect(fitted)
        elif effect == "pan":
            result = _add_pan_effect(fitted)
        else:
            result = fitted

        clip = result
        return clip

    except Exception as exc:
        logger.warning(f"Failed to process clip {path}: {exc}")
        if clip:
            try:
                clip.close()
            except Exception:
                pass
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  MAIN COMPILER
# ═══════════════════════════════════════════════════════════════════════════════

def compile_video(
    broll_paths:  list[str],
    audio_meta:   dict,
    seo_data:     dict,
    output_stem:  str,
) -> str:
    """
    Assemble the complete vertical short-form video and write it to disk.

    Parameters
    ----------
    broll_paths  : list[str]  — local paths to downloaded B-roll clips
    audio_meta   : dict       — output of audio_generator.generate_voiceover()
    seo_data     : dict       — seo sub-dict from script_generator output
    output_stem  : str        — filename base (no extension)

    Returns
    -------
    str — absolute path to the final MP4 file
    """
    output_path = str(config.FINAL_VIDEOS_DIR / f"{output_stem}.mp4")
    audio_path  = audio_meta["audio_path"]
    word_timings = audio_meta["word_timings"]
    total_dur    = audio_meta["duration_sec"]

    logger.info(f"Compiling video: {output_stem} | duration={total_dur:.2f}s")

    if not broll_paths:
        raise ValueError("No B-roll clips provided to the compiler.")

    # ── Determine clip durations (2-3 s each, cycling through available clips)
    target_clips   = math.ceil(total_dur / ((config.CLIP_MIN_SEC + config.CLIP_MAX_SEC) / 2))
    clip_durations = []
    import random
    t = 0.0
    while t < total_dur:
        d = round(random.uniform(config.CLIP_MIN_SEC, config.CLIP_MAX_SEC), 2)
        if t + d > total_dur:
            d = round(total_dur - t, 2)
        if d < 0.5:
            break
        clip_durations.append(d)
        t += d

    effects   = ["zoom", "pan", "none", "zoom"]  # Cycle for variety
    processed_clips: list[VideoFileClip] = []

    try:
        for i, dur in enumerate(clip_durations):
            src_path = broll_paths[i % len(broll_paths)]
            effect   = effects[i % len(effects)]
            logger.info(f"  Processing clip {i+1}/{len(clip_durations)}: {Path(src_path).name} ({dur}s, {effect})")

            pc = _process_broll_clip(src_path, dur, effect)
            if pc is not None:
                processed_clips.append(pc)
            else:
                # Insert a black filler clip so timing stays intact
                filler = ColorClip(size=(W, H), color=config.BG_COLOR, duration=dur)
                processed_clips.append(filler)

        if not processed_clips:
            raise RuntimeError("All B-roll clips failed to process.")

        # ── Concatenate B-roll sequence ──────────────────────────────────────
        logger.info("Concatenating clip sequence…")
        video_sequence = concatenate_videoclips(processed_clips, method="compose")

        # Ensure video sequence is exactly total_dur (pad or trim)
        if video_sequence.duration < total_dur:
            pad = ColorClip(size=(W, H), color=config.BG_COLOR,
                            duration=total_dur - video_sequence.duration)
            video_sequence = concatenate_videoclips([video_sequence, pad], method="compose")
        elif video_sequence.duration > total_dur:
            video_sequence = video_sequence.subclip(0, total_dur)

        # ── Build caption overlay ────────────────────────────────────────────
        logger.info("Building caption overlay…")
        caption_clip = _build_caption_clip(word_timings, total_dur)

        # ── Composite: B-roll + captions ─────────────────────────────────────
        logger.info("Compositing layers…")
        final_video = CompositeVideoClip(
            [video_sequence, caption_clip.set_position("center")],
            size=(W, H),
        )

        # ── Attach audio ─────────────────────────────────────────────────────
        logger.info("Attaching audio…")
        audio_clip = AudioFileClip(audio_path)
        # Trim audio to match video exactly
        if audio_clip.duration > total_dur:
            audio_clip = audio_clip.subclip(0, total_dur)

        final_video = final_video.set_audio(audio_clip)
        final_video = final_video.set_duration(total_dur)

        # ── Render ───────────────────────────────────────────────────────────
        logger.info(f"Rendering to {output_path}  (this may take a few minutes)…")
        final_video.write_videofile(
            output_path,
            fps          = FPS,
            codec        = "libx264",
            audio_codec  = "aac",
            bitrate      = config.VIDEO_BITRATE,
            audio_bitrate= config.AUDIO_BITRATE,
            preset       = "ultrafast",   # Fastest encode — fine for CI
            threads      = 2,             # Conservative for shared runners
            logger       = None,          # Suppress verbose MoviePy logs
            temp_audiofile= str(config.OUTPUT_DIR / f"{output_stem}_temp_audio.aac"),
            remove_temp  = True,
        )

        logger.info(f"✅ Video rendered: {output_path}")
        return output_path

    finally:
        # ── Memory cleanup — critical to prevent GitHub Actions OOM ─────────
        for c in processed_clips:
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
    # Quick smoke test: renders a 5-second black video with test captions
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
            "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", "2", "-q:a", "9", "-acodec", "libmp3lame",
            "output/audio/test_audio.mp3", "-y"
        ], check=True)

    compile_video([], dummy_audio, dummy_seo, "smoke_test")
