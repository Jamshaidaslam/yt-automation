import os, logging, random
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip, concatenate_videoclips, TextClip
import moviepy.video.fx.all as vfx
from moviepy.audio.fx.all import audio_loop

logger = logging.getLogger(__name__)

TARGET_WIDTH = 720
TARGET_HEIGHT = 1280

def compile_final_video(video_clips_paths, voiceover_data, bgm_file_path, output_path):
    logger.info("🎬 Initializing final audio-visual composite...")

    # 1. Audio Processing
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    duration = voice_clip.duration
    audio_tracks = [voice_clip]
    
    if bgm_file_path and os.path.exists(bgm_file_path):
        bgm_raw = AudioFileClip(bgm_file_path)
        bgm_clip = audio_loop(bgm_raw, duration=duration).volumex(0.06)
        audio_tracks.append(bgm_clip)
    final_audio = CompositeAudioClip(audio_tracks)

    # 2. Visual Processing (Fast Cuts)
    processed_clips = []
    available_clips = list(video_clips_paths)
    random.shuffle(available_clips)
    
    clip_dur = 2.5 # Fast cuts
    for path in available_clips:
        try:
            clip = VideoFileClip(path).without_audio()
            clip = clip.resize(height=TARGET_HEIGHT).crop(x_center=TARGET_WIDTH//2, width=TARGET_WIDTH, height=TARGET_HEIGHT)
            clip = clip.fx(vfx.resize, lambda t: 1.0 + (0.05 * t))
            processed_clips.append(clip.set_duration(clip_dur))
            if sum(c.duration for c in processed_clips) >= duration:
                break
        except Exception as e:
            logger.error(f"Clip error: {e}")

    # 3. Final Composite (FIXED NAME ERROR)
    final_video_concat = concatenate_videoclips(processed_clips, method="compose")
    
    # Text Caption Fix (Screen ke andar rahega)
    txt_clip = TextClip(
        "MASTER THE SILENCE", 
        fontsize=60, color='yellow', font='Arial-Bold', 
        method='caption', size=(TARGET_WIDTH - 100, None)
    ).set_pos('center').set_duration(duration)
    
    # Yahan 'final_video_concat' use kiya hai, 'video' nahi
    final_composite = CompositeVideoClip([final_video_concat, txt_clip])
    final_composite = final_composite.set_audio(final_audio).set_duration(duration)

    # 4. Rendering
    logger.info(f"🚀 Rendering to: {output_path}")
    final_composite.write_videofile(
        output_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast"
    )
    
    final_composite.close()
    voice_clip.close()
