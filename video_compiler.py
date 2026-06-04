"""
video_compiler.py — Production Compositor Engine (MOVIEPY AUTOMATED ENGINE v4.7)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import logging
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

logger = logging.getLogger(__name__)

def compile_final_video(video_clips_paths: list, voiceover_data: dict, bgm_file_path: str, output_path: str):
    logger.info("🎬 Initializing final audio-visual composite blending layers...")
    
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    bgm_clip = None

    # Safe dynamic inclusion gate for background score
    if bgm_file_path and os.path.exists(bgm_file_path) and os.path.getsize(bgm_file_path) > 20000:
        try:
            logger.info(f"🎵 Blending cinematic active background score: {Path(bgm_file_path).name}")
            bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration).volumex(0.04)
            final_audio = CompositeAudioClip([voice_clip, bgm_clip])
        except Exception as audio_err:
            logger.warning(f"⚠️ Audio device driver parsing failed on BGM. Switching to pure voice tracker. Error: {audio_err}")
            final_audio = CompositeAudioClip([voice_clip])
            bgm_clip = None
    else:
        logger.warning("⚠️ No valid BGM file path resolved. Processing with pure voice footprint.")
        final_audio = CompositeAudioClip([voice_clip])

    loaded_clips = [VideoFileClip(p).without_audio() for p in video_clips_paths]
    stitched_video = concatenate_videoclips(loaded_clips, method="compose").subclip(0, duration)
    
    w, h = stitched_video.size
    target_w = int(h * (9 / 16))
    x1 = (w - target_w) // 2
    cropped_video = stitched_video.crop(x1=x1, y1=0, x2=x1+target_w, y2=h)

    text_clips = []
    word_timings = voiceover_data["word_timings"]
    
    chunk_size = 2
    for i in range(0, len(word_timings), chunk_size):
        chunk = word_timings[i:i+chunk_size]
        if not chunk: continue
        
        chunk_text = " ".join([item["word"] for item in chunk])
        start_time = chunk[0]["start"]
        end_time = chunk[-1]["end"]
        
        text_color = "#FFFF00" if "WAIT" in chunk_text.upper() else ("#00FF00" if i % 4 == 0 else "#FFFFFF")
        
        txt_clip = (TextClip(chunk_text, font="Impact", fontsize=52, color=text_color, 
                             stroke_color="black", stroke_width=2.5, method="caption",
                             size=(target_w - 60, None))
                    .set_start(start_time)
                    .set_end(end_time)
                    .set_position(('center', 'center')))
        text_clips.append(txt_clip)

    final_composite = CompositeVideoClip([cropped_video] + text_clips).set_audio(final_audio)

    logger.info(f"🚀 Launching production compiler encoding engine -> Target: {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None
    )

    final_composite.close()
    cropped_video.close()
    stitched_video.close()
    for c in loaded_clips: c.close()
    voice_clip.close()
    if bgm_clip: bgm_clip.close()
    logger.info("✅ Final high-retention video compiled flawlessly!")
