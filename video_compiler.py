"""
video_compiler.py — Production Compositor Engine (PRODUCTION CORE v7.0 - SMOOTH ZOOM & FAST CUTS)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import logging
import warnings
import numpy as np
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

warnings.filterwarnings("ignore", category=UserWarning, module="moviepy")
logger = logging.getLogger(__name__)

def apply_kinetic_zoom(clip, zoom_speed=0.04):
    """Applies a high-retention cinematic subtle zoom-in effect over time."""
    def filter_frame(get_frame, t):
        frame = get_frame(t)
        h, w, c = frame.shape
        
        # Calculate current zoom factor linearly over time
        zoom = 1.0 + (zoom_speed * t)
        
        # Compute new box dimensions
        new_h, new_w = int(h / zoom), int(w / zoom)
        
        # Calculate bounding box anchors (centered)
        top = (h - new_h) // 2
        left = (w - new_w) // 2
        
        # Crop the center bounding matrix
        cropped_frame = frame[top:top+new_h, left:left+new_w]
        
        # Resize back to original target resolution using simple step scaling
        from PIL import Image
        img = Image.fromarray(cropped_frame)
        resized_img = img.resize((w, h), Image.Resampling.LANCZOS)
        return np.array(resized_img)
        
    return clip.fl(filter_frame)

def compile_final_video(video_clips_paths: list, voiceover_data: dict, bgm_file_path: str, output_path: str):
    logger.info("🎬 Initializing dynamic motion composite compilation matrix...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    logger.info(f"⏱️ Video baseline timeline locked to: {duration} seconds.")
    
    bgm_clip = None
    if bgm_file_path and os.path.exists(bgm_file_path) and os.path.getsize(bgm_file_path) > 20000:
        try:
            bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration).volumex(0.05)
            final_audio = CompositeAudioClip([voice_clip, bgm_clip])
        except Exception as audio_err:
            logger.warning(f"⚠️ BGM dropped: {audio_err}")
            final_audio = CompositeAudioClip([voice_clip])
    else:
        final_audio = CompositeAudioClip([voice_clip])

    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920

    logger.info("📐 Processing asset loops with cinematic motion tracking...")
    processed_clips = []
    
    # Calculate uniform clip length for fast cuts based on 12 scenes
    clip_slice_duration = max(2.5, duration / max(1, len(video_clips_paths)))

    for path in video_clips_paths:
        if not path or not os.path.exists(path):
            continue
        try:
            clip = VideoFileClip(path).without_audio().set_duration(clip_slice_duration)
            clip_resized = clip.resize(height=TARGET_HEIGHT)
            w, h = clip_resized.size
            x_center = w // 2
            clip_cropped = clip_resized.crop(x1=x_center - (TARGET_WIDTH // 2), y1=0, 
                                             x2=x_center + (TARGET_WIDTH // 2), y2=TARGET_HEIGHT)
            
            # Apply smooth zoom effect to every clip node individually
            zoomed_clip = apply_kinetic_zoom(clip_cropped, zoom_speed=0.05)
            processed_clips.append(zoomed_clip)
        except Exception as clip_err:
            logger.error(f"⚠️ Clip mapping failure [{path}]: {clip_err}")

    if not processed_clips:
        from moviepy.editor import ColorClip
        processed_clips.append(ColorClip(size=(TARGET_WIDTH, TARGET_HEIGHT), color=(15, 15, 15)).set_duration(duration))

    base_stitched = concatenate_videoclips(processed_clips, method="chain")
    stitched_video = base_stitched.loop(duration=duration)

    font_asset_path = "fonts/AmericanCaptain-MdEY.otf"
    if not os.path.exists(font_asset_path):
        font_asset_path = "Impact"

    text_clips = []
    word_timings = voiceover_data["word_timings"]
    chunk_size = 2
    
    for i in range(0, len(word_timings), chunk_size):
        chunk = word_timings[i:i+chunk_size]
        if not chunk or chunk[0]["start"] >= duration: 
            continue
        
        chunk_text = " ".join([item["word"] for item in chunk]).upper()
        start_time = chunk[0]["start"]
        end_time = min(chunk[-1]["end"], duration)
        
        text_color = "#00FF00" if i % 4 == 0 else "#FFFFFF"
        if any(k in chunk_text for k in ["PHONE", "DARK", "MIND", "TRAP", "CONTROL", "WATCHING"]):
            text_color = "#FFFF00" # High-contrast yellow retention markers
        
        try:
            txt_clip = (TextClip(chunk_text, font=font_asset_path, fontsize=85, color=text_color, 
                                 stroke_color="black", stroke_width=6.0, method="caption",
                                 size=(TARGET_WIDTH - 200, None))
                        .set_start(start_time)
                        .set_end(end_time)
                        .set_position(('center', TARGET_HEIGHT * 0.65)))
            text_clips.append(txt_clip)
        except Exception as text_err:
            logger.error(f"❌ Subtitle frame fail [{chunk_text}]: {text_err}")

    final_composite = CompositeVideoClip([stitched_video] + text_clips, size=(TARGET_WIDTH, TARGET_HEIGHT)).set_audio(final_audio)

    logger.info(f"🚀 Encoding production asset -> Target: {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="6000k",
        threads=4,
        preset="ultrafast",
        logger=None
    )

    final_composite.close()
    stitched_video.close()
    base_stitched.close()
    for c in processed_clips:
        try: c.close()
        except: pass
    voice_clip.close()
    logger.info("✅ High-retention short engineered cleanly.")
