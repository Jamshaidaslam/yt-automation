"""
video_compiler.py — Core Video Rendering Engine (FAST-CUT ZOOM + ANTI-SPAM BGM)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import logging
import textwrap
import random
import requests
import tempfile
import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoClip,
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    CompositeAudioClip,
)
from moviepy.video.fx.all import crop, resize
import moviepy.audio.fx.all as afx
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

W   = config.VIDEO_WIDTH    # 1080
H   = config.VIDEO_HEIGHT   # 1920
FPS = config.VIDEO_FPS      # 30

FONT_SIZE = 95
CAPTION_YELLOW_COLOR = (255, 255, 0, 255)
CAPTION_GREEN_COLOR  = (57, 255, 20, 255)
CAPTION_STROKE_COLOR = (0, 0, 0, 255)

MUSIC_DIR = Path("assets/music")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

# Auto Dark Music — Pixabay free tracks (commercial use allowed)
DARK_MUSIC_URLS = [
    "https://cdn.pixabay.com/download/audio/2022/10/25/audio_946bc6b590.mp3",
    "https://cdn.pixabay.com/download/audio/2023/03/09/audio_c8c8a73467.mp3",
    "https://cdn.pixabay.com/download/audio/2022/08/02/audio_884fe92c21.mp3",
    "https://cdn.pixabay.com/download/audio/2023/01/26/audio_d16737dc28.mp3",
    "https://cdn.pixabay.com/download/audio/2022/11/22/audio_febc508520.mp3",
]


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        font_name = getattr(config, "FONT_NAME", None) or getattr(config, "FONT_FILE", "Impact.ttf")
        font_path = config.FONTS_DIR / font_name
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def _download_random_dark_music(duration: float) -> str | None:
    """Pixabay se random dark music download karo — har video pe alag."""
    random.shuffle(DARK_MUSIC_URLS)
    for url in DARK_MUSIC_URLS:
        try:
            logger.info(f"Downloading dark music track from Pixabay...")
            response = requests.get(url, timeout=30, stream=True)
            if response.status_code == 200:
                tmp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3", dir=str(MUSIC_DIR)
                )
                for chunk in response.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                tmp.close()
                logger.info(f"✅ Dark music downloaded: {tmp.name}")
                return tmp.name
        except Exception as e:
            logger.warning(f"Music download failed, trying next: {e}")
            continue
    logger.warning("All music downloads failed — using local track if available.")
    return None


def _get_music_track(duration: float) -> str | None:
    """Pehle local tracks check karo, phir online download karo."""
    local_tracks = [
        f for f in list(MUSIC_DIR.glob("*.mp3")) + list(MUSIC_DIR.glob("*.wav"))
        if not f.name.startswith("tmp")
    ]
    if local_tracks:
        selected = random.choice(local_tracks)
        logger.info(f"🎵 Local music track selected: {selected.name}")
        return str(selected)

    downloaded = _download_random_dark_music(duration)
    if downloaded:
        return downloaded

    return None


def _render_caption_frame_cached(t: float, word_timings: list[dict]) -> np.ndarray:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    active_word = ""
    adjusted_time = t + 0.18

    for item in word_timings:
        if item["start"] <= adjusted_time <= item["end"]:
            active_word = item["word"].upper().strip()
            break

    if not active_word:
        return np.array(img)

    font = _get_font(FONT_SIZE)
    current_y = int(H * 0.45)

    bbox = draw.textbbox((0, 0), active_word, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (W - text_w) // 2

    text_color = CAPTION_GREEN_COLOR if len(active_word) > 5 else CAPTION_YELLOW_COLOR

    for adj_x, adj_y in [(-6, -6), (6, -6), (-6, 6), (6, 6), (-4, 0), (4, 0), (0, -4), (0, 4)]:
        draw.text(
            (x + adj_x, current_y + adj_y),
            active_word, font=font, fill=CAPTION_STROKE_COLOR
        )

    draw.text((x, current_y), active_word, font=font, fill=text_color)
    return np.array(img)


def compile_video(media_paths: list[str], voiceover_data: dict, output_stem: str) -> str:
    logger.info("Starting video compilation engine with Fast-Cut Aggressive Zoom...")
    final_path   = config.FINAL_VIDEOS_DIR / f"{output_stem}.mp4"
    total_dur    = voiceover_data["duration_sec"]
    word_timings = voiceover_data["word_timings"]
    downloaded_music = None

    if not media_paths:
        raise ValueError("Cannot compile video — media paths list is empty.")

    video_clips        = []
    allocated_raw_clips = []
    current_time       = 0.0
    media_index        = 0
    bg_audio           = None

    try:
        MAX_CLIP_DURATION = 2.5

        while current_time < total_dur:
            path_str  = media_paths[media_index % len(media_paths)]
            media_index += 1

            clip_path = Path(path_str)
            if not clip_path.exists():
                continue

            raw_clip = VideoFileClip(str(clip_path), audio=False)
            allocated_raw_clips.append(raw_clip)

            rem_dur       = total_dur - current_time
            clip_duration = min(raw_clip.duration, rem_dur, MAX_CLIP_DURATION)

            if clip_duration <= 0.3:
                continue

            sub_clip    = raw_clip.subclip(0, clip_duration)
            clip_w, clip_h = sub_clip.size
            target_ratio   = W / H
            current_ratio  = clip_w / clip_h

            # VERTICAL CROP (9:16 Center Aspect Ratio Fix)
            if current_ratio > target_ratio:
                new_w    = int(clip_h * target_ratio)
                sub_clip = crop(sub_clip, x_center=clip_w // 2, width=new_w, height=clip_h)
            elif current_ratio < target_ratio:
                new_h    = int(clip_w / target_ratio)
                sub_clip = crop(sub_clip, y_center=clip_h // 2, width=clip_w, height=new_h)

            # Standard scale mapping
            processed_clip = resize(sub_clip, newsize=(W, H))

            # 🔥 FAST-CUT AGGRESSIVE ZOOM EFFECT (Ken Burns Niche Hack)
            # 0.05 se badha kar 0.12 kar diya hai taake short duration clips par zoom tezi se aur saaf nazar aaye
            processed_clip = processed_clip.resize(lambda t: 1.0 + 0.12 * t)

            video_clips.append(processed_clip)
            current_time += clip_duration

        if not video_clips:
            raise RuntimeError("No visual media clips processed successfully.")

        # 'compose' method hierarchy dynamic placement ke liye zaroori hai
        video_sequence = concatenate_videoclips(
