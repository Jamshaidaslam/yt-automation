"""
video_compiler.py — Elite Production Compositor Engine (v10.5 - FINAL)
Optimized for 1-Word Chunk Retention & Mobile Padding
"""

import os
import logging
import warnings
import numpy as np
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip
from moviepy.video.fx.all import crop, fadeout

# Suppress warnings for clean execution
warnings.filterwarnings("ignore", category=UserWarning, module="moviepy")
logger = logging.getLogger(__name__)

# ─── VIRAL SETTINGS ──────────────────────────────────────────────────────────
CAPTION_Y_PX = 1300          # Fixed Y position for mobile safe zone
CAPTION_FONT_SIZE = 82
CAPTION_COLOR = "#FFD700"
CAPTION_HIGHLIGHT_COLOR = "#FFFF00"  # Neon Red for impact
HIGHLIGHT_KEYWORDS = {
    "TRAP", "TRAPPED", "DARK", "SECRET", "SECRETS", "CONTROL", "CONTROLS",
    "MANIPULATE", "MANIPULATION", "DOPAMINE", "ADDICTED", "ADDICTION",
    "HACK", "HACKING", "FEAR", "ANXIETY", "DANGEROUS", "DANGER",
    "TRUTH", "EXPOSED", "SHOCKING", "WARNING", "STOP", "FOLLOW", "SAVE"
}

def apply_dynamic_motion_scale(clip, zoom_ratio=0.06):
    """Applies continuous zoom transformation."""
    def transform_matrix_frame(get_frame, t):
        frame = get_frame(t)
        h, w, c = frame.shape
        scale_factor = 1.0 + (zoom_ratio * t)
        box_h, box_w = int(h / scale_factor), int(w / scale_factor)
        y_offset, x_offset = (h - box_h) // 2, (w - box_w) // 2
        matrix_crop = frame[y_offset:y_offset+box_h, x_offset:x_offset+box_w]
        from PIL import Image
        return np.array(Image.fromarray(matrix_crop).resize((w, h), Image.Resampling.BICUBIC))
    return clip.fl(transform_matrix_frame)

def apply_text_pop_effect(txt_clip, pop_duration=0.08):
    """Creates kinetic pop effect for words."""
    def text_filter(get_frame, t):
        frame = get_frame(t)
        h, w, c = frame.shape
        scale = 0.70 + (0.30 * (t / pop_duration)) if t < pop_duration else 1.0
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        from PIL import Image
        pil_img = Image.fromarray(frame).resize((new_w, new_h), Image.Resampling.BICUBIC)
        out_frame = np.zeros((h, w, c), dtype=np.uint8)
        pad_x, pad_y = (w - new_w) // 2, (h - new_h) // 2
        out_frame[pad_y:pad_y+new_h, pad_x:pad_x+new_w] = np.array(pil_img)
        return out_frame
    return txt_clip.fl(text_filter)

def compile_final_video(video_clips_paths, voiceover_data, bgm_file_path, output_path):
    logger.info("🎬 Initializing v10.5 Viral Compositor...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Audio Setup
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    final_audio = CompositeAudioClip([voice_clip])
    
    # 2. Process Video Clips
    processed_clips = []
    clip_slice = max(2.5, (duration / max(1, len(video_clips_paths))) + 0.1)
    
    for path in video_clips_paths:
        if os.path.exists(path):
            clip = VideoFileClip(path).without_audio().set_duration(clip_slice)
            # Resize and Center Crop
            clip = clip.resize(height=1920) if clip.h < clip.w else clip.resize(width=1080)
            clip = crop(clip, width=1080, height=1920, x_center=clip.w/2, y_center=clip.h/2)
            processed_clips.append(apply_dynamic_motion_scale(clip, 0.05))

    base_stitched = concatenate_videoclips(processed_clips, method="chain").set_duration(duration)
    
    # 3. Captioning Matrix
    text_clips = []
    font = "Arial-Bold" 
    chunk_size = 1 # AGGRESSIVE 1-WORD CHUNK
    
    for i in range(0, len(voiceover_data["word_timings"]), chunk_size):
        chunk = voiceover_data["word_timings"][i:i+chunk_size]
        txt = " ".join([item["word"] for item in chunk]).upper()
        
        # Highlight logic
        color = CAPTION_HIGHLIGHT_COLOR if (set(txt.split()) & HIGHLIGHT_KEYWORDS) else CAPTION_COLOR
        
        txt_clip = TextClip(
            txt, font=font, fontsize=CAPTION_FONT_SIZE, 
            color=color, stroke_color="black", stroke_width=9, 
            size=(880, None), method="caption"
        )
        
        # Timing and Animation
        txt_clip = apply_text_pop_effect(
            txt_clip.set_start(chunk[0]["start"]).set_end(chunk[-1]["end"]), 
            0.07
        )
        text_clips.append(txt_clip.set_position(("center", CAPTION_Y_PX)))

    # 4. Final Render
    final = CompositeVideoClip([base_stitched] + text_clips, size=(1080, 1920)).set_audio(final_audio)
    
    logger.info(f"🚀 Writing video to: {output_path}")
    final.write_videofile(
        output_path, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac", 
        bitrate="7500k", 
        preset="ultrafast", 
        logger=None
    )
    
    # Clean up
    final.close()
    base_stitched.close()
    voice_clip.close()
    logger.info("✅ Final video compiled successfully.")
