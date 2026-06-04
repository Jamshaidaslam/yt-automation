import os, logging, random
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    CompositeAudioClip, concatenate_videoclips, TextClip
)
import moviepy.video.fx.all as vfx
from moviepy.audio.fx.all import audio_loop
from PIL import Image, ImageDraw, ImageFont
import config

# PIL compatibility fix
try:
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    pass

logger = logging.getLogger(__name__)

# ─── Configuration ───────────────────────────────────────────────────────────
TARGET_WIDTH, TARGET_HEIGHT = 720, 1280
MIN_DURATION, MAX_DURATION = 35, 55
FAST_CUT_DUR = 2.0

def _build_caption_clips(voiceover_data, total_duration):
    """ Builds caption clips with a strict fail-safe. """
    caption_clips = []
    words_data = voiceover_data.get("word_timings", [])
    if not words_data: return []

    chunks = [words_data[i:i+3] for i in range(0, len(words_data), 3)]
    for chunk in chunks:
        try:
            # Check if ImageMagick is available/working by trying to render a simple clip
            txt = TextClip(
                " ".join(c["word"] for c in chunk), fontsize=72, color='yellow',
                font="Arial-Bold", method="caption", size=(640, None), 
                stroke_color="black", stroke_width=3
            ).set_start(chunk[0]["start"]).set_duration(max(chunk[-1]["end"]-chunk[0]["start"], 0.3)).set_pos("center")
            caption_clips.append(txt)
        except Exception:
            # If TextClip fails, we skip captions instead of crashing the whole pipeline
            continue
    return caption_clips

def generate_thumbnail(video_clip, title_text, output_path):
    try:
        # Get frame safely
        img = Image.fromarray(video_clip.get_frame(1.0)).resize((TARGET_WIDTH, TARGET_HEIGHT))
        font_path = str(config.FONTS_DIR / config.FONT_NAME)
        font = ImageFont.truetype(font_path, 72) if os.path.exists(font_path) else ImageFont.load_default()
        
        ImageDraw.Draw(img).text((50, TARGET_HEIGHT - 200), title_text[:40], font=font, fill=(255, 230, 0))
        thumb_path = output_path.replace(".mp4", "_thumbnail.jpg")
        img.save(thumb_path, "JPEG")
        return thumb_path
    except Exception as e:
        logger.warning(f"Thumbnail generation skipped: {e}")
        return None

def compile_final_video(video_clips_paths, voiceover_data, bgm_file_path, output_path, title_text="Watch Till End"):
    try:
        logger.info("🎬 Starting Compilation...")
        voice_clip = AudioFileClip(voiceover_data["audio_path"])
        duration = min(max(voice_clip.duration, MIN_DURATION), MAX_DURATION)
        
        # Audio
        audio_tracks = [voice_clip]
        if bgm_file_path and isinstance(bgm_file_path, str) and os.path.exists(bgm_file_path):
            audio_tracks.append(audio_loop(AudioFileClip(bgm_file_path), duration=duration).volumex(0.06))
        
        # Video
        processed_clips = []
        total_dur = 0.0
        random.shuffle(video_clips_paths)
        
        for path in video_clips_paths:
            if total_dur >= duration: break
            if path and os.path.exists(path):
                try:
                    clip = VideoFileClip(path).without_audio()
                    clip = clip.resize(height=TARGET_HEIGHT).crop(x_center=TARGET_WIDTH/2, width=TARGET_WIDTH, height=TARGET_HEIGHT)
                    clip = clip.fx(vfx.resize, lambda t: 1.0 + 0.03 * t)
                    cut = min(FAST_CUT_DUR, duration - total_dur)
                    processed_clips.append(clip.subclip(0, cut).set_duration(cut))
                    total_dur += cut
                except: continue
        
        if not processed_clips:
            return None, None

        final_video_concat = concatenate_videoclips(processed_clips, method="compose")
        
        # Composite with Captions (Captions are optional/fail-safe)
        captions = _build_caption_clips(voiceover_data, duration)
        final_composite = CompositeVideoClip([final_video_concat] + captions).set_audio(CompositeAudioClip(audio_tracks)).set_duration(duration)
        
        # Write file
        final_composite.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
        
        thumb = generate_thumbnail(final_composite, title_text, output_path)
        
        # Manual cleanup of memory
        final_composite.close()
        final_video_concat.close()
        voice_clip.close()
        
        return str(output_path), thumb
    
    except Exception as e:
        logger.error(f"Critical error in compile_final_video: {e}")
        return None, None
