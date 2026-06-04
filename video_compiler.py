"""
video_compiler.py — Production Compositor Engine (FINAL v7.0 - STABLE)
AI Dark Realities · Short-Form Video Pipeline
────────────────────────────────────────────────────────────────────────────
Features:
  1. Kinetic Zoom-In Effect (Ken Burns) on every B-roll clip.
  2. Multi-Color Dynamic Subtitles (Green/Blue/Yellow) with Pop-Zoom.
  3. Optimized Threading for GitHub Actions (RAM efficient).
  4. YUV420p Pixel Format for universal social media compatibility.
"""

import os
import logging
import random
from pathlib import Path
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, 
    CompositeAudioClip, concatenate_videoclips
)
import moviepy.video.fx.all as vfx
import config

logger = logging.getLogger(__name__)

TARGET_WIDTH = 720
TARGET_HEIGHT = 1280

def _resolve_font() -> str:
    # Font resolution for Linux server environment
    return "DejaVu-Sans-Bold"

def compile_final_video(video_clips_paths: list, voiceover_data: dict, bgm_file_path: str, output_path: str):
    logger.info("🎬 Initializing final audio-visual composite...")

    # 1. Audio Pipeline
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    audio_tracks = [voice_clip]
    
    if bgm_file_path and os.path.exists(bgm_file_path):
        bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration).volumex(0.06)
        audio_tracks.append(bgm_clip)
    
    final_audio = CompositeAudioClip(audio_tracks)

    # 2. Visual Engine (Fast-Cutting & Kinetic Zoom)
    word_timings = voiceover_data["word_timings"]
    processed_clips = []
    available_clips = list(video_clips_paths)
    random.shuffle(available_clips)
    clip_index = 0

    # Sync chunks (Fast cutting: ~5 words per clip)
    for i in range(0, len(word_timings), 5):
        chunk = word_timings[i : i + 5]
        phrase_start, phrase_end = chunk[0]["start"], chunk[-1]["end"]
        phrase_duration = max(phrase_end - phrase_start, 1.5)

        selected_clip_path = available_clips[clip_index % len(available_clips)]
        clip_index += 1

        try:
            raw_clip = VideoFileClip(selected_clip_path).without_audio()
            # Loop/Crop logic
            sub_clip = raw_clip.loop(duration=phrase_duration) if raw_clip.duration < phrase_duration else raw_clip.subclip(0, phrase_duration)
            
            # 🔥 KINETIC ZOOM: Slow zoom-in effect
            sub_clip = sub_clip.fx(vfx.resize, lambda t: 1.0 + (0.1 * (t / phrase_duration)))
            
            # Center Crop
            clip_final = sub_clip.resize(height=TARGET_HEIGHT).crop(x_center=TARGET_WIDTH//2, width=TARGET_WIDTH, height=TARGET_HEIGHT)
            processed_clips.append(clip_final.set_start(phrase_start).set_end(phrase_end))
        except Exception as e:
            logger.error(f"Clip render error: {e}")

    # 3. Text/Caption Engine (Pop-Zoom Effect)
    text_clips = []
    font = _resolve_font()
    
    for i in range(0, len(word_timings), 3):
        chunk = word_timings[i: i + 3]
        txt = " ".join([item["word"] for item in chunk]).upper()
        
        # Color rotation
        colors = ["#00FF00", "#00FFFF", "#FFFF00"]
        color = colors[(i // 3) % 3]
        
        txt_clip = TextClip(txt, font=font, fontsize=70, color=color, stroke_color="black", stroke_width=4, method="caption", size=(600, None)) \
            .set_start(chunk[0]["start"]).set_end(chunk[-1]["end"]) \
            .set_position("center") \
            .fx(vfx.resize, lambda t: 0.8 + 0.2 * (t < 0.2)) # Pop effect
        
        text_clips.append(txt_clip)

    # 4. Final Render
    final_video = CompositeVideoClip([concatenate_videoclips(processed_clips, method="compose")] + text_clips, size=(TARGET_WIDTH, TARGET_HEIGHT))
    final_video = final_video.set_audio(final_audio).set_duration(duration)

    # 🔥 Render with safety flags
    final_video.write_videofile(
        output_path, fps=24, codec="libx264", audio_codec="aac", 
        preset="ultrafast", pixel_format="yuv420p", ffmpeg_params=["-crf", "28", "-movflags", "+faststart"]
    )
    
    # Cleanup
    final_video.close()
    voice_clip.close()
