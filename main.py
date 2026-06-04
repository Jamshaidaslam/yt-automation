import os, logging, random
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    CompositeAudioClip, concatenate_videoclips, TextClip
)
import moviepy.video.fx.all as vfx
from moviepy.audio.fx.all import audio_loop
from PIL import Image, ImageDraw, ImageFont
import config

try:
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    pass

logger = logging.getLogger(__name__)

TARGET_WIDTH, TARGET_HEIGHT = 720, 1280
MIN_DURATION, MAX_DURATION = 35, 55
FAST_CUT_DUR = 2.0

def _build_caption_clips(voiceover_data, total_duration):
    caption_clips = []
    words_data = voiceover_data.get("word_timings", [])
    if not words_data:
        text = voiceover_data.get("text", "")
        words = text.split()
        if not words: return []
        word_dur = total_duration / len(words)
        words_data = [{"word": w, "start": i*word_dur, "end": (i+1)*word_dur} for i, w in enumerate(words)]

    chunks = [words_data[i:i+3] for i in range(0, len(words_data), 3)]
    for idx, chunk in enumerate(chunks):
        txt = TextClip(
            " ".join(c["word"] for c in chunk), fontsize=72, color='yellow',
            font="Arial-Bold", method="caption", size=(640, None), stroke_color="black", stroke_width=3
        ).set_start(chunk[0]["start"]).set_duration(max(chunk[-1]["end"]-chunk[0]["start"], 0.3)).set_pos("center")
        caption_clips.append(txt)
    return caption_clips

def generate_thumbnail(video_clip, title_text, output_path):
    try:
        img = Image.fromarray(video_clip.get_frame(1.0)).resize((TARGET_WIDTH, TARGET_HEIGHT))
        font_path = str(config.FONTS_DIR / config.FONT_NAME)
        font = ImageFont.truetype(font_path, 72) if os.path.exists(font_path) else ImageFont.load_default()
        ImageDraw.Draw(img).text((50, TARGET_HEIGHT - 200), title_text, font=font, fill=(255, 230, 0))
        thumb_path = output_path.replace(".mp4", "_thumbnail.jpg")
        img.save(thumb_path, "JPEG")
        return thumb_path
    except: return None

def compile_final_video(video_clips_paths, voiceover_data, bgm_file_path, output_path, title_text):
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = min(max(voice_clip.duration, MIN_DURATION), MAX_DURATION)
    
    audio_tracks = [voice_clip]
    if bgm_file_path and isinstance(bgm_file_path, str) and os.path.exists(bgm_file_path):
        audio_tracks.append(audio_loop(AudioFileClip(bgm_file_path), duration=duration).volumex(0.06))
    
    processed_clips = []
    total_dur = 0.0
    random.shuffle(video_clips_paths)
    for path in video_clips_paths:
        if total_dur >= duration: break
        if path and os.path.exists(path):
            try:
                clip = VideoFileClip(path).without_audio().resize(height=TARGET_HEIGHT).crop(x_center=TARGET_WIDTH/2, width=TARGET_WIDTH, height=TARGET_HEIGHT)
                cut = min(FAST_CUT_DUR, duration - total_dur)
                processed_clips.append(clip.subclip(0, cut).set_duration(cut))
                total_dur += cut
            except: continue
            
    final_video = concatenate_videoclips(processed_clips, method="compose")
    final_composite = CompositeVideoClip([final_video] + _build_caption_clips(voiceover_data, duration)).set_audio(CompositeAudioClip(audio_tracks)).set_duration(duration)
    final_composite.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    
    thumb = generate_thumbnail(final_composite, title_text, output_path)
    final_composite.close()
    voice_clip.close()
    return str(output_path), thumb
