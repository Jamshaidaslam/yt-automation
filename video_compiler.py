"""
video_compiler.py — Production Compositor Engine (MOVIEPY AUTOMATED ENGINE v4.6)
AI Dark Realities · Short-Form Video Pipeline
Fixed: Aligned single-file BGM pipeline mapping to prevent encoding exit breaks.
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import logging
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

logger = logging.getLogger(__name__)

def compile_final_video(video_clips_paths: list, voiceover_data: dict, bgm_file_path: str, output_path: str):
    """Composes B-rolls, deep voiceprints, auto-ducked music, and ultra-high-retention single line caption chunks."""
    logger.info("🎬 Initializing final audio-visual composite blending layers...")
    
    # Load voiceover
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration

    # 1. Background Music (BGM) Target Layer Injection
    if not os.path.exists(bgm_file_path) or os.path.getsize(bgm_file_path) == 0:
        raise FileNotFoundError(f"Target BGM file asset missing or corrupt at layout node: {bgm_file_path}")
    
    logger.info(f"🎵 Blending cinematic active background score: {Path(bgm_file_path).name}")
    bgm_clip = AudioFileClip(bgm_file_path).loop(duration=duration)
    
    # -22dB Dynamic Attenuation Rule for crystal-clear voice footprint
    bgm_clip = bgm_clip.volumex(0.05) 

    final_audio = CompositeAudioClip([voice_clip, bgm_clip])

    # 2. B-Roll Stitching and Vertical Aspect Clipping Engine
    loaded_clips = [VideoFileClip(p).without_audio() for p in video_clips_paths]
    stitched_video = concatenate_videoclips(loaded_clips, method="compose").subclip(0, duration)
    
    # Force absolute 9:16 vertical delivery ratios
    w, h = stitched_video.size
    target_w = int(h * (9 / 16))
    x1 = (w - target_w) // 2
    cropped_video = stitched_video.crop(x1=x1, y1=0, x2=x1+target_w, y2=h)

    # 3. Dynamic Word Chunking Subtitles Engine (High-Retention Text Pacing)
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

    # Blend all layers together seamlessly
    final_composite = CompositeVideoClip([cropped_video] + text_clips).set_audio(final_audio)

    # Output final compiled render stream
    logger.info(f"🚀 Launching production compiler encoding engine -> Target: {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None
    )

    # Cleanup resources safely to prevent memory leaks or locking crashes
    final_composite.close()
    cropped_video.close()
    stitched_video.close()
    for c in loaded_clips: c.close()
    voice_clip.close()
    bgm_clip.close()
    logger.info("✅ Final high-retention video compiled flawlessly!")
