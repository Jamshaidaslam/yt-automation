"""
video_compiler.py — Core Video Rendering Engine v3.8 (SUSPENSE TRAP EDITION)
AI Dark Realities · Short-Form Video Pipeline
Fixed: Programmatic center position override, 1.6x scale burst, and GOLD color flash for "WAIT..."
Fixed: Real-time audio music ducking during the hook silence freeze frame to maximize tension.
Tested: Bracket alignment and Python 3.10+ syntax error-free.
──────────────────────────────────────────────
"""

import logging
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
    ImageClip,
)
from moviepy.video.fx.all import crop, resize
import moviepy.audio.fx.all as afx
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

W = config.VIDEO_WIDTH
H = config.VIDEO_HEIGHT
FPS = config.VIDEO_FPS

FONT_SIZE = 95
CAPTION_YELLOW_COLOR = (255, 255, 0, 255)
CAPTION_GOLD_COLOR = (255, 215, 0, 255) # Premium Gold for the Trap
CAPTION_GREEN_COLOR = (57, 255, 20, 255)
CAPTION_WHITE_COLOR = (255, 255, 255, 255)
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

def _get_font(size):
    try:
        font_name = getattr(config, "FONT_NAME", None) or getattr(config, "FONT_FILE", "Impact.ttf")
        font_path = config.FONTS_DIR / font_name
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def _download_random_dark_music(duration):
    random.shuffle(DARK_MUSIC_URLS)
    for url in DARK_MUSIC_URLS:
        try:
            logger.info("Downloading dark music track from Pixabay...")
            response = requests.get(url, timeout=30, stream=True)
            if response.status_code == 200:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=str(MUSIC_DIR))
                for chunk in response.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                tmp.close()
                logger.info("✅ Dark music downloaded: " + tmp.name)
                return tmp.name
        except Exception as e:
            logger.warning("Music download failed, trying next: " + str(e))
            continue
    return None

def _get_music_track(duration):
    local_tracks = [f for f in list(MUSIC_DIR.glob("*.mp3")) + list(MUSIC_DIR.glob("*.wav")) if not f.name.startswith("tmp")]
    if local_tracks:
        selected = random.choice(local_tracks)
        logger.info("🎵 Local music track selected: " + selected.name)
        return str(selected)
    downloaded = _download_random_dark_music(duration)
    if downloaded:
        return downloaded
    return None

def _render_caption_frame_cached(t, word_timings):
    """
    Renders word by word subtitles with DYNAMIC POSITIONING and KINETIC ZOOM.
    Overrides everything when the hook "WAIT..." trap is triggered.
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    active_word = ""
    word_index = 0
    word_start = 0.0
    word_end = 0.0
    adjusted_time = t
    
    for idx, item in enumerate(word_timings):
        if item["start"] <= adjusted_time <= item["end"]:
            active_word = item["word"].upper().strip()
            word_index = idx
            word_start = item["start"]
            word_end = item["end"]
            break
            
    if not active_word:
        return np.array(img)
        
    # CRITICAL TRIGGER INTERCEPTOR: "WAIT..." Hook Check
    is_trap_word = "WAIT" in active_word

    if is_trap_word:
        # Hard lock to screen exact CENTER during the silence trap
        base_y = int(H * 0.48)
        text_color = CAPTION_GOLD_COLOR
    else:
        # Dynamic positioning loop for regular content flow
        random.seed(word_index + 99)
        position_choice = random.choice(['bottom', 'center', 'top'])
        
        if position_choice == 'bottom':
            base_y = int(H * 0.75)
            text_color = CAPTION_WHITE_COLOR
        elif position_choice == 'top':
            base_y = int(H * 0.20)
            text_color = CAPTION_GREEN_COLOR
        else:
            base_y = int(H * 0.45)
            text_color = CAPTION_YELLOW_COLOR

    # Kinetic Zoom Scale Config
    word_duration = max(0.05, word_end - word_start)
    progress = (adjusted_time - word_start) / word_duration
    
    if is_trap_word:
        # Massive screen burst effect for the hook trap (Starts at 1.1x and scales up to 1.6x)
        zoom_factor = 1.1 + (0.5 * (progress / 1.0))
    else:
        if progress < 0.25:
            zoom_factor = 1.0 + (0.25 * (progress / 0.25))
        else:
            zoom_factor = 1.25
        
    dynamic_font_size = int(FONT_SIZE * zoom_factor)
    font = _get_font(dynamic_font_size)
    
    bbox = draw.textbbox((0, 0), active_word, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Extreme screen retention shaker math
    if is_trap_word:
        shake_x = random.randint(-6, 6) # Extra violent shake for the freeze text
        shake_y = random.randint(-4, 4)
    else:
        shake_x = random.randint(-4, 4)
        shake_y = random.randint(-2, 2)
    
    x = (W - text_w) // 2 + shake_x
    current_y = base_y - (text_h // 2) + shake_y
    
    # Bold premium black border layout rendering
    stroke_thickness = 8 if is_trap_word else 6
    for adj_x, adj_y in [(-stroke_thickness, -stroke_thickness), (stroke_thickness, -stroke_thickness), 
                         (-stroke_thickness, stroke_thickness), (stroke_thickness, stroke_thickness), 
                         (-stroke_thickness, 0), (stroke_thickness, 0), (0, -stroke_thickness), (0, stroke_thickness)]:
        draw.text((x + adj_x, current_y + adj_y), active_word, font=font, fill=CAPTION_STROKE_COLOR)
        
    draw.text((x, current_y), active_word, font=font, fill=text_color)
    return np.array(img)

def compile_video(media_paths, voiceover_data, output_stem):
    logger.info("Starting video compilation engine with SUSPENSE COGNITIVE SYNC...")
    final_path = config.FINAL_VIDEOS_DIR / (output_stem + ".mp4")
    THUMB_DURATION = 1.0
    voice_dur = voiceover_data["duration_sec"]
    potential_thumb = config.FINAL_VIDEOS_DIR / ("thumb_" + output_stem + ".jpg")
    has_thumb = potential_thumb.exists()
    total_dur = voice_dur + (THUMB_DURATION if has_thumb else 0.0)
    word_timings = voiceover_data["word_timings"]
    downloaded_music = None

    if not media_paths:
        raise ValueError("Cannot compile video — media paths list is empty.")

    video_clips = []
    allocated_raw_clips = []
    current_time = 0.0
    media_index = 0
    bg_audio = None
    thumb_clip = None

    try:
        MAX_CLIP_DURATION = 2.5
        while current_time < voice_dur:
            path_str = media_paths[media_index % len(media_paths)]
            media_index += 1
            clip_path = Path(path_str)
            if not clip_path.exists():
                continue
            raw_clip = VideoFileClip(str(clip_path), audio=False)
            allocated_raw_clips.append(raw_clip)
            rem_dur = voice_dur - current_time
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
            processed_clip = processed_clip.resize(lambda t: 1.0 + 0.12 * t)
            video_clips.append(processed_clip)
            current_time += clip_duration

        if not video_clips:
            raise RuntimeError("No visual media clips processed successfully.")

        video_sequence = concatenate_videoclips(video_clips, method="compose")

        voice_audio = AudioFileClip(voiceover_data["audio_path"])
        voice_audio = afx.volumex(voice_audio, 1.0)
        music_path = _get_music_track(total_dur)

        if music_path:
            logger.info("🎵 Injecting adaptive dark music track with custom trap ducking...")
            bg_audio = AudioFileClip(music_path)
            if music_path.startswith(str(MUSIC_DIR)) and "tmp" in music_path:
                downloaded_music = music_path
            if bg_audio.duration < total_dur:
                bg_audio = afx.audio_loop(bg_audio, duration=total_dur)
            else:
                bg_audio = bg_audio.subclip(0, total_dur)
            
            # --- DYNAMIC SUSPENSE AUDIO DUCKING LOGIC ---
            # Dhoondte hain ke WAIT lafz kab se kab tak hai timeline pe
            trap_start, trap_end = None, None
            for item in word_timings:
                if "WAIT" in item["word"].upper():
                    trap_start = item["start"]
                    trap_end = item["end"]
                    break

            if trap_start is not None and trap_end is not None:
                # Custom lambda wrapper jo specific suspense trap timeframe par volume ko 90% mazeed drop kar dega
                if has_thumb:
                    adjusted_start = trap_start + THUMB_DURATION
                    adjusted_end = trap_end + THUMB_DURATION
                else:
                    adjusted_start = trap_start
                    adjusted_end = trap_end

                def volume_ducking_filter(gf, t):
                    # gf(t) is a numpy array of shape (N, 2) for stereo audio frames
                    factor = np.ones_like(t) * 0.25 # Base dark music volume (25%)
                    # Sannata region logic check
                    duck_mask = (t >= adjusted_start) & (t <= adjusted_end)
                    factor[duck_mask] = 0.02 # Intense drop to 2% volume for dramatic shock
                    
                    # Convert to column vectors for element-wise array multiplication
                    return gf(t) * factor[:, np.newaxis]
                
                bg_audio = bg_audio.fl(volume_ducking_filter, keep_duration=True)
                logger.info(f"🔒 Audio compression ducking filter locked on frame sequence [{trap_start}s - {trap_end}s]")
            else:
                bg_audio = afx.volumex(bg_audio, 0.25)
            
            if has_thumb:
                voice_audio = voice_audio.set_start(THUMB_DURATION)
            final_audio = CompositeAudioClip([voice_audio, bg_audio])
        else:
            logger.warning("No music available — rendering with voice only.")
            if has_thumb:
                voice_audio = voice_audio.set_start(THUMB_DURATION)
            final_audio = voice_audio

        if has_thumb:
            logger.info(f"🎨 HD Thumbnail found: {potential_thumb.name}. Merging...")
            thumb_clip = (ImageClip(str(potential_thumb))
                          .set_duration(THUMB_DURATION)
                          .set_fps(FPS)
                          .resize(newsize=(W, H)))
            final_visual_sequence = concatenate_videoclips([thumb_clip, video_sequence], method="compose")
        else:
            final_visual_sequence = video_sequence

        final_visual_sequence = final_visual_sequence.set_audio(final_audio)

        def make_caption_frame(t):
            adjusted_t = t - THUMB_DURATION if has_thumb else t
            frame = _render_caption_frame_cached(adjusted_t, word_timings)
            return frame[:, :, :3]

        def make_caption_mask(t):
            adjusted_t = t - THUMB_DURATION if has_thumb else t
            frame = _render_caption_frame_cached(adjusted_t, word_timings)
            return frame[:, :, 3] / 255.0

        caption_clip = VideoClip(make_caption_frame, duration=total_dur).set_fps(FPS)
        caption_mask = VideoClip(make_caption_mask, ismask=True, duration=total_dur).set_fps(FPS)
        caption_clip = caption_clip.set_mask(caption_mask)

        final_layers = [final_visual_sequence, caption_clip]
        final_video = CompositeVideoClip(final_layers, size=(W, H))
        final_video = final_video.set_duration(total_dur)

        logger.info(f"Rendering output file to -> {final_path}")
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

        if has_thumb:
            try:
                logger.info("🎬 Formatting metadata cover art for Instagram...")
                temp_output = str(final_path).replace(".mp4", "_meta.mp4")
                ffmpeg_cmd = (
                    f'ffmpeg -y -i "{final_path}" -i "{potential_thumb}" '
                    f'-map 0 -map 1 -c copy -disposition:v:1 attached_pic '
                    f'"{temp_output}"'
                )
                exit_code = os.system(ffmpeg_cmd)
                if exit_code == 0:
                    os.replace(temp_output, str(final_path))
                    logger.info("✅ Hybrid Cover System locked successfully!")
            except Exception as meta_err:
                logger.error(f"❌ Hybrid metadata error: {meta_err}")

        return str(final_path)

    finally:
        for c in video_clips:
            try: c.close()
            except Exception: pass
        for rc in allocated_raw_clips:
            try: rc.close()
            except Exception: pass
        for name in ("video_sequence", "caption_clip", "caption_mask", "final_visual_sequence",
                     "final_video", "voice_audio", "bg_audio", "final_audio", "thumb_clip"):
            obj = locals().get(name)
            if obj is not None:
                try: 
                    obj.close()
                except Exception: 
                    pass
        if downloaded_music and os.path.exists(downloaded_music):
            try:
                os.remove(downloaded_music)
                logger.info("Temp music file cleaned up.")
            except Exception:
                pass
