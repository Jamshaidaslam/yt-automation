import os, logging, random
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    CompositeAudioClip, concatenate_videoclips, TextClip
)
import moviepy.video.fx.all as vfx
from moviepy.audio.fx.all import audio_loop
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import config

# Fix for PIL ANTIALIAS error in newer versions
try:
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    pass

logger = logging.getLogger(__name__)

# ─── Configuration ───────────────────────────────────────────────────────────
TARGET_WIDTH = 720
TARGET_HEIGHT = 1280
MIN_DURATION = 35
MAX_DURATION = 55
FAST_CUT_DUR = 2.0
CAPTION_COLORS = ["#00FF00", "#FFFF00"]
CAPTION_POSITIONS = ["top", "center", "bottom"]
WORDS_PER_CAPTION = 3
CAPTION_FONTSIZE = 72

def _build_caption_clips(voiceover_data, total_duration):
    caption_clips = []
    words_data = voiceover_data.get("word_timings", [])

    if not words_data:
        text = voiceover_data.get("text", "")
        words = text.split()
        if not words: return []
        word_dur = total_duration / len(words)
        words_data = [{"word": w, "start": i * word_dur, "end": (i + 1) * word_dur} for i, w in enumerate(words)]

    chunks = [words_data[i:i + WORDS_PER_CAPTION] for i in range(0, len(words_data), WORDS_PER_CAPTION)]
    
    random.seed(42)
    positions_cycle = CAPTION_POSITIONS.copy()
    random.shuffle(positions_cycle)

    for idx, chunk in enumerate(chunks):
        chunk_text = " ".join(c["word"] for c in chunk)
        chunk_start = chunk[0]["start"]
        chunk_end = chunk[-1]["end"]
        chunk_dur = max(chunk_end - chunk_start, 0.3)
        color = CAPTION_COLORS[idx % len(CAPTION_COLORS)]
        position = positions_cycle[idx % len(positions_cycle)]

        pos_arg = ("center", 80) if position == "top" else (("center", TARGET_HEIGHT - 180) if position == "bottom" else "center")

        try:
            txt = TextClip(
                chunk_text, fontsize=CAPTION_FONTSIZE, color=color,
                font="Arial-Bold", method="caption", size=(TARGET_WIDTH - 80, None),
                stroke_color="black", stroke_width=3
            ).set_start(chunk_start).set_duration(chunk_dur).set_pos(pos_arg)
            caption_clips.append(txt)
        except Exception as e:
            logger.warning(f"Caption failed: {e}")
    return caption_clips

def generate_thumbnail(video_clip, title_text, output_path):
    try:
        frame = video_clip.get_frame(1.0)
        img = Image.fromarray(frame).resize((TARGET_WIDTH, TARGET_HEIGHT))
        draw = ImageDraw.Draw(img)
        # Use font from config
        font_path = str(config.FONTS_DIR / config.FONT_NAME)
        font = ImageFont.truetype(font_path, 72) if os.path.exists(font_path) else ImageFont.load_default()
        
        draw.text((50, TARGET_HEIGHT - 200), title_text, font=font, fill=(255, 230, 0))
        thumb_path = output_path.replace(".mp4", "_thumbnail.jpg")
        img.save(thumb_path, "JPEG")
        return thumb_path
    except Exception as e:
        logger.error(f"Thumb failed: {e}")
        return None

def compile_final_video(video_clips_paths, voiceover_data, bgm_file_path, output_path, title_text="Watch Till End"):
    logger.info("🎬 Compilation Started...")
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = min(max(voice_clip.duration, MIN_DURATION), MAX_DURATION)
    
    # Music
    audio_tracks = [voice_clip]
    if bgm_file_path and os.path.exists(bgm_file_path):
        bgm = audio_loop(AudioFileClip(bgm_file_path), duration=duration).volumex(0.06)
        audio_tracks.append(bgm)
    final_audio = CompositeAudioClip(audio_tracks)

    # Clips
    processed_clips = []
    total_video_dur = 0.0
    random.shuffle(video_clips_paths)
    
    for path in video_clips_paths:
        if total_video_dur >= duration: break
        try:
            clip = VideoFileClip(path).without_audio().resize(height=TARGET_HEIGHT).crop(x_center=TARGET_WIDTH/2, width=TARGET_WIDTH, height=TARGET_HEIGHT)
            clip = clip.fx(vfx.resize, lambda t: 1.0 + 0.03 * t)
            cut_dur = min(FAST_CUT_DUR, duration - total_video_dur)
            processed_clips.append(clip.subclip(0, cut_dur).set_duration(cut_dur))
            total_video_dur += cut_dur
        except: continue

    final_video_concat = concatenate_videoclips(processed_clips, method="compose")
    
    # Final Composite
    layers = [final_video_concat] + _build_caption_clips(voiceover_data, duration)
    final_composite = CompositeVideoClip(layers, size=(TARGET_WIDTH, TARGET_HEIGHT)).set_audio(final_audio).set_duration(duration)
    
    final_composite.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    
    # Thumb
    generate_thumbnail(final_composite, title_text, output_path)
    
    final_composite.close()
    voice_clip.close()
