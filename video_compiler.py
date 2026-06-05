"""
video_compiler.py — Elite Production Compositor Engine (PRODUCTION CORE v9.5 - TIMESYNC FIXED)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import random
import logging
import warnings
import numpy as np
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

warnings.filterwarnings("ignore", category=UserWarning, module="moviepy")
logger = logging.getLogger(__name__)

def apply_dynamic_motion_scale(clip, zoom_ratio=0.06):
    def transform_matrix_frame(get_frame, t):
        frame = get_frame(t)
        h, w, c = frame.shape
        scale_factor = 1.0 + (zoom_ratio * t)
        box_h, box_w = int(h / scale_factor), int(w / scale_factor)
        y_offset = (h - box_h) // 2
        x_offset = (w - box_w) // 2
        matrix_crop = frame[y_offset:y_offset+box_h, x_offset:x_offset+box_w]
        from PIL import Image
        pil_img = Image.fromarray(matrix_crop)
        resized_img = pil_img.resize((w, h), Image.Resampling.BICUBIC)
        return np.array(resized_img)
    return clip.fl(transform_matrix_frame)

def apply_text_pop_effect(txt_clip, pop_duration=0.08):
    def text_filter(get_frame, t):
        frame = get_frame(t)
        h, w, c = frame.shape
        if t < pop_duration:
            scale = 0.65 + (0.35 * (t / pop_duration))
        else:
            scale = 1.0
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        from PIL import Image
        pil_img = Image.fromarray(frame)
        resized_img = pil_img.resize((new_w, new_h), Image.Resampling.BICUBIC)
        out_frame = np.zeros((h, w, c), dtype=np.uint8)
        pad_x = max(0, (w - new_w) // 2)
        pad_y = max(0, (h - new_h) // 2)
        render_w = min(new_w, w - pad_x)
        render_h = min(new_h, h - pad_y)
        out_frame[pad_y:pad_y+render_h, pad_x:pad_x+render_w] = np.array(resized_img)[0:render_h, 0:render_w]
        return out_frame
    return txt_clip.fl(text_filter)

def compile_final_video(video_clips_paths: list, voiceover_data: dict, bgm_file_path: str, output_path: str):
    logger.info("🎬 Initializing time-synced audio-visual compositor matrix...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    
    bgm_clip = None
    if bgm_file_path and os.path.exists(bgm_file_path) and os.path.getsize(bgm_file_path) > 20000:
        try:
            bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration).volumex(0.04)
            final_audio = CompositeAudioClip([voice_clip, bgm_clip])
        except:
            final_audio = CompositeAudioClip([voice_clip])
    else:
        final_audio = CompositeAudioClip([voice_clip])

    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920
    processed_clips = []
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
            motion_clip = apply_dynamic_motion_scale(clip_cropped, zoom_ratio=0.05)
            processed_clips.append(motion_clip)
        except Exception as ce:
            logger.error(f"⚠️ Discarding node clip asset: {ce}")

    if not processed_clips:
        from moviepy.editor import ColorClip
        processed_clips.append(ColorClip(size=(TARGET_WIDTH, TARGET_HEIGHT), color=(15, 15, 15)).set_duration(duration))

    base_stitched = concatenate_videoclips(processed_clips, method="compose")
    stitched_video = base_stitched.loop(duration=duration)

    font_asset_path = "fonts/AmericanCaptain-MdEY.otf"
    if not os.path.exists(font_asset_path):
        font_asset_path = "Impact"

    text_clips = []
    word_timings = voiceover_data["word_timings"]
    chunk_size = 2 # 2 words together for standard dynamic reel loops
    
    vertical_positions = [
        int(TARGET_HEIGHT * 0.22), # Top
        int(TARGET_HEIGHT * 0.46), # Center
        int(TARGET_HEIGHT * 0.70)  # Bottom
    ]
    last_pos = -1

    for i in range(0, len(word_timings), chunk_size):
        chunk = word_timings[i:i+chunk_size]
        if not chunk or chunk[0]["start"] >= duration: 
            continue
        
        chunk_text = " ".join([item["word"] for item in chunk]).upper()
        start_time = chunk[0]["start"]
        # 🔥 CRITICAL FIX: Ensure the end_time is locked strictly to the next chunk's start or word end
        end_time = min(chunk[-1]["end"], duration)
        
        # Prevent caption lingering text overlaps
        if (i + chunk_size) < len(word_timings):
            end_time = min(end_time, word_timings[i + chunk_size]["start"])

        # Safety padding for dynamic jumps
        if end_time <= start_time:
            end_time = start_time + 0.3

        text_color = "#FFFFFF"
        if i % 3 == 0: text_color = "#00FF00"
        if any(k in chunk_text for k in ["PHONE", "DARK", "MIND", "TRAP", "CONTROL", "CONTROLS", "PSYCHOLOGY", "SECRET", "YOU", "TOOL"]):
            text_color = "#FFFF00"

        available_positions = [p for idx, p in enumerate(vertical_positions) if idx != last_pos]
        chosen_y = random.choice(available_positions)
        last_pos = vertical_positions.index(chosen_y)

        try:
            txt_clip = (TextClip(chunk_text, font=font_asset_path, fontsize=95, color=text_color, 
                                 stroke_color="black", stroke_width=6.0, method="caption",
                                 size=(TARGET_WIDTH - 240, None))
                        .set_start(start_time)
                        .set_end(end_time))
            
            animated_txt = apply_text_pop_effect(txt_clip, pop_duration=0.07)
            positioned_txt = animated_txt.set_position(('center', chosen_y))
            text_clips.append(positioned_txt)
        except Exception as text_err:
            logger.error(f"❌ Subtitle failure [{chunk_text}]: {text_err}")

    final_composite = CompositeVideoClip([stitched_video] + text_clips, size=(TARGET_WIDTH, TARGET_HEIGHT)).set_audio(final_audio)

    logger.info(f"🚀 Launching hardware compile output -> Target: {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="7000k",
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
    if bgm_clip: bgm_clip.close()
    logger.info("✅ Fluid Time-Synced Short Compiled Successfully.")
