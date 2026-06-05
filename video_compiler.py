"""
video_compiler.py — Production Compositor Engine (PRODUCTION CORE v5.7 - FORCE PATH)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import logging
import warnings
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

warnings.filterwarnings("ignore", category=UserWarning, module="moviepy")
logger = logging.getLogger(__name__)

def compile_final_video(video_clips_paths: list, voiceover_data: dict, bgm_file_path: str, output_path: str):
    logger.info("🎬 Initializing final audio-visual composite layers...")
    
    # Force output directory setup just in case
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = min(voice_clip.duration, 59.0)
    logger.info(f"⏱️ Video execution timeline locked to: {duration} seconds.")
    
    bgm_clip = None
    if bgm_file_path and os.path.exists(bgm_file_path) and os.path.getsize(bgm_file_path) > 20000:
        try:
            logger.info(f"🎵 Blending background score: {Path(bgm_file_path).name}")
            bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration).volumex(0.05)
            final_audio = CompositeAudioClip([voice_clip.set_duration(duration), bgm_clip])
        except Exception as audio_err:
            logger.warning(f"⚠️ BGM dropped: {audio_err}")
            final_audio = CompositeAudioClip([voice_clip.set_duration(duration)])
    else:
        final_audio = CompositeAudioClip([voice_clip.set_duration(duration)])

    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920

    logger.info("📐 Normalizing and cropping stock stream stack...")
    processed_clips = []
    
    for path in video_clips_paths:
        try:
            clip = VideoFileClip(path, target_resolution=(TARGET_HEIGHT, None)).without_audio()
            clip_resized = clip.resize(height=TARGET_HEIGHT)
            w, h = clip_resized.size
            x_center = w // 2
            clip_cropped = clip_resized.crop(x1=x_center - (TARGET_WIDTH // 2), y1=0, 
                                             x2=x_center + (TARGET_WIDTH // 2), y2=TARGET_HEIGHT)
            processed_clips.append(clip_cropped)
        except Exception as clip_err:
            logger.error(f"⚠️ Skipping clip node [{path}]: {clip_err}")

    if not processed_clips:
        raise RuntimeError("CRITICAL: No visual clips parsed.")

    base_stitched = concatenate_videoclips(processed_clips, method="chain")
    stitched_video = base_stitched.loop(duration=duration)

    text_clips = []
    word_timings = voiceover_data["word_timings"]
    chunk_size = 2
    
    for i in range(0, len(word_timings), chunk_size):
        chunk = word_timings[i:i+chunk_size]
        if not chunk or chunk[0]["start"] >= duration: continue
        
        chunk_text = " ".join([item["word"] for item in chunk]).upper()
        start_time = chunk[0]["start"]
        end_time = min(chunk[-1]["end"], duration)
        
        text_color = "#FFFF00" if any(k in chunk_text for k in ["WAIT", "SECRET", "DARK", "MIND"]) else ("#00FF00" if i % 4 == 0 else "#FFFFFF")
        
        txt_clip = (TextClip(chunk_text, font="Impact", fontsize=65, color=text_color, 
                             stroke_color="black", stroke_width=5.0, method="caption",
                             size=(TARGET_WIDTH - 300, None))
                    .set_start(start_time)
                    .set_end(end_time)
                    .set_position(('center', TARGET_HEIGHT * 0.65)))
        text_clips.append(txt_clip)

    final_composite = CompositeVideoClip([stitched_video] + text_clips, size=(TARGET_WIDTH, TARGET_HEIGHT)).set_audio(final_audio)

    logger.info(f"🚀 Launching encoding sequence -> Target: {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="4500k",
        threads=4,
        preset="ultrafast",
        logger=None
    )

    final_composite.close()
    stitched_video.close()
    base_stitched.close()
    for c in processed_clips: c.close()
    voice_clip.close()
    if bgm_clip: bgm_clip.close()
    logger.info("✅ Short asset compiled flawlessly.")
