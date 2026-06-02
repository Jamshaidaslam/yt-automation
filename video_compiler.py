"""
video_compiler.py — Core Video Rendering Engine (FAST-CUT ZOOM + FIXED FFMPEG OUTPUT)
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
    ImageClip,  # 🌟 Added to inject first-frame visual thumbnail
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
    return None


def _get_music_track(duration: float) -> str | None:
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
    
    # 🔥 FIXED OFFSET LOGIC: Captions synced perfectly to pop up 1.8s early
    adjusted_time = t - 1.8

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

            # Strict Hard Crop - Eliminating side grey bars and padding completely
            if current_ratio > target_ratio:
                new_w    = int(clip_h * target_ratio)
                sub_clip = crop(sub_clip, x_center=clip_w // 2, width=new_w, height=clip_h)
            elif current_ratio < target_ratio:
                new_h    = int(clip_w / target_ratio)
                sub_clip = crop(sub_clip, y_center=clip_h // 2, width=clip_w, height=new_h)

            processed_clip = resize(sub_clip, newsize=(W, H))

            # FAST ZOOM EFFECT
            processed_clip = processed_clip.resize(lambda t: 1.0 + 0.12 * t)

            video_clips.append(processed_clip)
            current_time += clip_duration

        if not video_clips:
            raise RuntimeError("No visual media clips processed successfully.")

        video_sequence = concatenate_videoclips(video_clips, method="compose")

        # AUDIO PROCESSING
        voice_audio = AudioFileClip(voiceover_data["audio_path"])
        voice_audio = afx.volumex(voice_audio, 1.0)

        music_path = _get_music_track(total_dur)

        if music_path:
            logger.info(f"🎵 Injecting dark music track into video...")
            bg_audio = AudioFileClip(music_path)
            
            if music_path.startswith(str(MUSIC_DIR)) and "tmp" in music_path:
                downloaded_music = music_path
            else:
                downloaded_music = None

            if bg_audio.duration < total_dur:
                bg_audio = afx.audio_loop(bg_audio, duration=total_dur)
            else:
                bg_audio = bg_audio.subclip(0, total_dur)

            bg_audio     = afx.volumex(bg_audio, 0.25)
            final_audio  = CompositeAudioClip([voice_audio, bg_audio])
        else:
            logger.warning("No music available — rendering with voice only.")
            final_audio = voice_audio

        video_sequence = video_sequence.set_audio(final_audio)

        def make_caption_frame(t):
            frame = _render_caption_frame_cached(t, word_timings)
            return frame[:, :, :3]

        def make_caption_mask(t):
            frame = _render_caption_frame_cached(t, word_timings)
            return frame[:, :, 3] / 255.0

        caption_clip = VideoClip(make_caption_frame, duration=total_dur).set_fps(FPS)
        caption_mask = VideoClip(make_caption_mask, ismask=True, duration=total_dur).set_fps(FPS)
        caption_clip = caption_clip.set_mask(caption_mask)

        # 🌟 FEATURE: FIRST-FRAME THUMBNAIL INJECTION LAYER
        final_layers = [video_sequence]
        potential_thumb = config.FINAL_VIDEOS_DIR / f"thumb_{output_stem}.jpg"
        
        if potential_thumb.exists():
            logger.info(f"🎨 Custom Thumbnail found: {potential_thumb.name}. Injecting into first frame...")
            # Create a 0.15 second flash clip of the high retention thumbnail
            thumb_clip = (ImageClip(str(potential_thumb))
                          .set_duration(0.15)
                          .set_fps(FPS)
                          .set_position(('center', 'center')))
            
            # Layer the thumbnail flash over the start of the video sequence
            # MoviePy will keep the base video track timeline identical
            final_layers.append(thumb_clip.set_start(0.0))

        # Add Captions overlay layer
        final_layers.append(caption_clip)

        final_video = CompositeVideoClip(final_layers, size=(W, H))
        final_video = final_video.set_duration(total_dur)

        logger.info(f"Rendering compressed fast-cut short output file to -> {final_path}")

        final_video.write_videofile(
            str(final_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            bitrate="2500k",
            audio_bitrate="128k",
            preset="ultrafast",
            threads=2,
            logger=None
        )

        return str(final_path)

    finally:
        for c in video_clips:
            try: c.close()
            except Exception: pass
        for rc in allocated_raw_clips:
            try: rc.close()
            except Exception: pass
        for name in ("video_sequence", "caption_clip", "caption_mask",
                     "final_video", "voice_audio", "bg_audio", "final_audio", "thumb_clip"):
            obj = locals().get(name)
            if obj is not None:
                try: obj.close()
                except Exception: pass
        if downloaded_music and os.path.exists(downloaded_music):
            try:
                os.remove(downloaded_music)
                logger.info("Temp music file cleaned up.")
            except Exception:
                pass
