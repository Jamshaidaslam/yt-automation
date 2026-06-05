"""
video_compiler.py — Production Compositor Engine (PRODUCTION CORE v6.0 - BLACK FRAME & FONT FIX)
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
    logger.info("🎬 Initializing final audio-visual composite layer matrix...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    logger.info(f"⏱️ Video baseline timeline locked to voiceover length: {duration} seconds.")
    
    bgm_clip = None
    if bgm_file_path and os.path.exists(bgm_file_path) and os.path.getsize(bgm_file_path) > 20000:
        try:
            logger.info(f"🎵 Blending ambient background score: {Path(bgm_file_path).name}")
            bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration).volumex(0.06)
            final_audio = CompositeAudioClip([voice_clip, bgm_clip])
        except Exception as audio_err:
            logger.warning(f"⚠️ BGM dropped, using standalone voice narration: {audio_err}")
            final_audio = CompositeAudioClip([voice_clip])
    else:
        final_audio = CompositeAudioClip([voice_clip])

    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920

    logger.info("📐 Normalizing, cropping, and stitching visual assets pipeline...")
    processed_clips = []
    
    for path in video_clips_paths:
        if not path or not os.path.exists(path):
            continue
        try:
            clip = VideoFileClip(path).without_audio()
            clip_resized = clip.resize(height=TARGET_HEIGHT)
            w, h = clip_resized.size
            x_center = w // 2
            clip_cropped = clip_resized.crop(x1=x_center - (TARGET_WIDTH // 2), y1=0, 
                                             x2=x_center + (TARGET_WIDTH // 2), y2=TARGET_HEIGHT)
            processed_clips.append(clip_cropped)
        except Exception as clip_err:
            logger.error(f"⚠️ Skipping damaged clip node [{path}]: {clip_err}")

    if not processed_clips:
        logger.warning("⚠️ Empty clip stack arrays opened. Creating solid base layer...")
        from moviepy.editor import ColorClip
        processed_clips.append(ColorClip(size=(TARGET_WIDTH, TARGET_HEIGHT), color=(15, 15, 15)).set_duration(duration))

    # 🔥 FIX BLACK FRAMES: Stitch clips and loop them infinitely to fill the entire voiceover length
    base_stitched = concatenate_videoclips(processed_clips, method="chain")
    stitched_video = base_stitched.loop(duration=duration)

    # 🔥 FIX FONT LOADING: Explicitly mapping font asset file path link
    font_asset_path = "fonts/AmericanCaptain-MdEY.otf"
    if not os.path.exists(font_asset_path):
        logger.warning(f"⚠️ Custom font path '{font_asset_path}' not found! Falling back to Impact standard.")
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
        
        # High retention color styling maps
        text_color = "#FFFF00" if any(k in chunk_text for k in ["WAIT", "SECRET", "DARK", "MIND", "TRAP", "CONTROL"]) else ("#00FF00" if i % 4 == 0 else "#FFFFFF")
        
        try:
            txt_clip = (TextClip(chunk_text, font=font_asset_path, fontsize=75, color=text_color, 
                                 stroke_color="black", stroke_width=5.5, method="caption",
                                 size=(TARGET_WIDTH - 260, None))
                        .set_start(start_time)
                        .set_end(end_time)
                        .set_position(('center', TARGET_HEIGHT * 0.62)))
            text_clips.append(txt_clip)
        except Exception as text_err:
            logger.error(f"❌ Failed to render text frame chunk [{chunk_text}]: {text_err}")

    final_composite = CompositeVideoClip([stitched_video] + text_clips, size=(TARGET_WIDTH, TARGET_HEIGHT)).set_audio(final_audio)

    logger.info(f"🚀 Encoding high-retention cinematic short -> Target: {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",
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
    logger.info("✅ Pipeline compiled flawlessly without artifacts.")
