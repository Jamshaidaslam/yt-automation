"""
video_compiler.py — Production Compositor Engine (PRODUCTION CORE v5.3 - CLEAN SYNTAX)
AI Dark Realities · Short-Form Video Pipeline
Fixed: Totally sanitized and cleared from invisible non-printable character traps.
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import logging
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

logger = logging.getLogger(__name__)

def compile_final_video(video_clips_paths: list, voiceover_data: dict, bgm_file_path: str, output_path: str):
    logger.info("🎬 Initializing final audio-visual composite blending layers...")
    
    # 1. Base Audio Tracking Assets Setup
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    bgm_clip = None

    if bgm_file_path and os.path.exists(bgm_file_path) and os.path.getsize(bgm_file_path) > 20000:
        try:
            logger.info(f"🎵 Blending cinematic active background score: {Path(bgm_file_path).name}")
            bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration).volumex(0.05)
            final_audio = CompositeAudioClip([voice_clip, bgm_clip])
        except Exception as audio_err:
            logger.warning(f"⚠️ BGM parsing failed. Switching to pure voice tracker. Error: {audio_err}")
            final_audio = CompositeAudioClip([voice_clip])
            bgm_clip = None
    else:
        logger.warning("⚠️ No valid BGM file path resolved. Processing with pure voice footprint.")
        final_audio = CompositeAudioClip([voice_clip])

    # 2. Hardcoded Target Phone Dimensions (9:16 Vertical Short Profile Architecture)
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920

    # 3. Processing and Resizing B-Roll Elements Safely
    logger.info("📐 Compiling and normalizing raw stock clips into unified stream layer...")
    processed_clips = []
    
    for path in video_clips_paths:
        try:
            clip = VideoFileClip(path).without_audio()
            # Force scale asset up to maintain standard vertical format structure
            clip_resized = clip.resize(height=TARGET_HEIGHT)
            # Crop horizontal overflow to secure exact 1080 center alignment
            w, h = clip_resized.size
            x_center = w // 2
            clip_cropped = clip_resized.crop(x1=x_center - (TARGET_WIDTH // 2), y1=0, 
                                             x2=x_center + (TARGET_WIDTH // 2), y2=TARGET_HEIGHT)
            processed_clips.append(clip_cropped)
        except Exception as clip_err:
            logger.error(f"⚠️ Skipping damaged/corrupted B-roll asset node [{path}]: {clip_err}")

    if not processed_clips:
        raise RuntimeError("CRITICAL: Zero usable visual assets parsed. Video construction aborted.")

    # Pure B-Roll loop generator. Footage ab black screen par nahi jayegi, aakhir tak loop hogi.
    base_stitched = concatenate_videoclips(processed_clips, method="compose")
    stitched_video = base_stitched.loop(duration=duration)

    # 4. High-Retention Caption Wrapping Subtitles Engine
    text_clips = []
    word_timings = voiceover_data["word_timings"]
    
    # Chunking 2 words together for quick punchy reading retention loops
    chunk_size = 2
    for i in range(0, len(word_timings), chunk_size):
        chunk = word_timings[i:i+chunk_size]
        if not chunk: continue
        
        chunk_text = " ".join([item["word"] for item in chunk]).upper()
        start_time = chunk[0]["start"]
        end_time = chunk[-1]["end"]
        
        # Color coding triggers based on emotional phrasing nodes
        text_color = "#FFFF00" if "WAIT" in chunk_text or "SECRET" in chunk_text else ("#00FF00" if i % 4 == 0 else "#FFFFFF")
        
        # Safe margin layout width padding (TARGET_WIDTH - 300) taake text mobile screen se na kate
        txt_clip = (TextClip(chunk_text, font="Impact", fontsize=60, color=text_color, 
                             stroke_color="black", stroke_width=4.5, method="caption",
                             size=(TARGET_WIDTH - 300, None))
                    .set_start(start_time)
                    .set_end(end_time)
                    .set_position(('center', TARGET_HEIGHT * 0.65))) # Perfectly placed at lower third safe zone
        text_clips.append(txt_clip)

    # Compile the layout architecture together without black screen bleed leaks
    final_composite = CompositeVideoClip([stitched_video] + text_clips, size=(TARGET_WIDTH, TARGET_HEIGHT)).set_audio(final_audio)

    # 5. Master Render Out Execution Code
    logger.info(f"🚀 Launching production compiler encoding engine -> Target: {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
        logger=None
    )

    # Close operational file streams cleanly to clear process tracking memory
    final_composite.close()
    stitched_video.close()
    base_stitched.close()
    for c in processed_clips: c.close()
    voice_clip.close()
    if bgm_clip: bgm_clip.close()
    logger.info("✅ Final viral short asset compiled flawlessly without black background bleed!")
