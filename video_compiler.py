"""
video_compiler.py — Production Compositor Engine (v7.2 - CRASH FIXED)
Fixes: 
  1. Resolved 'AudioFileClip has no attribute size' error by separating Audio/Video logic.
  2. Simplified CompositeVideoClip initialization.
"""

import os, logging, random
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip, concatenate_videoclips
import moviepy.video.fx.all as vfx
from moviepy.audio.fx.all import audio_loop

logger = logging.getLogger(__name__)

TARGET_WIDTH = 720
TARGET_HEIGHT = 1280

def compile_final_video(video_clips_paths, voiceover_data, bgm_file_path, output_path):
    logger.info("🎬 Initializing final audio-visual composite blending layers...")

    # 1. Audio Processing (Separate Audio Layer)
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    audio_tracks = [voice_clip]
    
    if bgm_file_path and os.path.exists(bgm_file_path):
        try:
            bgm_raw = AudioFileClip(bgm_file_path)
            bgm_clip = audio_loop(bgm_raw, duration=duration).volumex(0.06)
            audio_tracks.append(bgm_clip)
        except Exception as e:
            logger.warning(f"⚠️ BGM error: {e}")

    final_audio = CompositeAudioClip(audio_tracks)

    # 2. Visual Processing (Separate Video Layer)
    processed_clips = []
    available_clips = list(video_clips_paths)
    random.shuffle(available_clips)
    
    clip_dur = duration / len(available_clips) if available_clips else duration
    
    for path in available_clips:
        try:
            clip = VideoFileClip(path).without_audio()
            # Resize, Crop, and Zoom effect
            clip = clip.resize(height=TARGET_HEIGHT).crop(x_center=TARGET_WIDTH//2, width=TARGET_WIDTH, height=TARGET_HEIGHT)
            clip = clip.fx(vfx.resize, lambda t: 1.0 + (0.05 * t))
            processed_clips.append(clip.set_duration(clip_dur))
        except Exception as e:
            logger.error(f"Clip processing error: {e}")

    # 3. Final Composite (Video and Audio joined here)
    # 🔥 FIXED: Sirf Video clips ko CompositeVideoClip mein dala hai
    final_video = concatenate_videoclips(processed_clips, method="compose")
    final_video = final_video.set_audio(final_audio).set_duration(duration)

    logger.info(f"🚀 Rendering to: {output_path}")
    
    final_video.write_videofile(
        output_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac", 
        preset="ultrafast", 
        logger=None,
        ffmpeg_params=[
            "-crf", "28", 
            "-pix_fmt", "yuv420p", 
            "-movflags", "+faststart"
        ]
    )
    
    # Cleanup
    final_video.close()
    voice_clip.close()
