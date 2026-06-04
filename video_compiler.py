import os
import logging
import random
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    CompositeAudioClip, concatenate_videoclips, TextClip
)
import moviepy.video.fx.all as vfx
from moviepy.audio.fx.all import audio_loop
from PIL import Image, ImageDraw, ImageFont
import numpy as np

logger = logging.getLogger(__name__)

# ─── Canvas Size (Vertical/Shorts) ───────────────────────────────────────────
TARGET_WIDTH  = 720
TARGET_HEIGHT = 1280

# ─── Duration Target ─────────────────────────────────────────────────────────
MIN_DURATION = 35   # seconds
MAX_DURATION = 55   # seconds

# ─── Caption Config ───────────────────────────────────────────────────────────
CAPTION_COLORS    = ["#00FF00", "#FFFF00"]   # Green & Yellow
CAPTION_POSITIONS = ["top", "center", "bottom"]
WORDS_PER_CAPTION = 3                         # 3 words at a time
CAPTION_FONTSIZE  = 72
CAPTION_FONT      = "Arial-Bold"

# ─── Fast-Cut Duration per clip ───────────────────────────────────────────────
FAST_CUT_DUR = 2.0   # seconds per clip (fast cuts)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER: Build word-caption clips
# ══════════════════════════════════════════════════════════════════════════════
def _build_caption_clips(voiceover_data, total_duration):
    """
    Break transcript into 3-word chunks and render each as a TextClip.
    Color cycles between Green & Yellow.
    Position cycles randomly among top / center / bottom.
    """
    caption_clips = []

    words_data = voiceover_data.get("word_timings", [])

    # ── Fallback: if no word_timings, split evenly ────────────────────────────
    if not words_data:
        text = voiceover_data.get("text", "")
        if not text:
            return []
        words = text.split()
        if not words:
            return []
        word_dur = total_duration / len(words)
        words_data = [
            {"word": w, "start": i * word_dur, "end": (i + 1) * word_dur}
            for i, w in enumerate(words)
        ]

    # ── Group into chunks of WORDS_PER_CAPTION ────────────────────────────────
    chunks = [words_data[i:i + WORDS_PER_CAPTION]
              for i in range(0, len(words_data), WORDS_PER_CAPTION)]

    random.seed(42)   # reproducible position sequence
    positions_cycle = CAPTION_POSITIONS.copy()
    random.shuffle(positions_cycle)

    for idx, chunk in enumerate(chunks):
        if not chunk:
            continue

        chunk_text  = " ".join(c["word"] for c in chunk)
        chunk_start = chunk[0]["start"]
        chunk_end   = chunk[-1]["end"]
        chunk_dur   = max(chunk_end - chunk_start, 0.3)

        color    = CAPTION_COLORS[idx % len(CAPTION_COLORS)]
        position = positions_cycle[idx % len(positions_cycle)]

        # ── Map position string to (x, y) ────────────────────────────────────
        if position == "top":
            pos_arg = ("center", 80)
        elif position == "bottom":
            pos_arg = ("center", TARGET_HEIGHT - 180)
        else:  # center
            pos_arg = "center"

        try:
            txt = (
                TextClip(
                    chunk_text,
                    fontsize=CAPTION_FONTSIZE,
                    color=color,
                    font=CAPTION_FONT,
                    method="caption",
                    size=(TARGET_WIDTH - 80, None),
                    stroke_color="black",
                    stroke_width=3,
                )
                .set_start(chunk_start)
                .set_duration(chunk_dur)
                .set_pos(pos_arg)
            )
            caption_clips.append(txt)
        except Exception as e:
            logger.warning(f"Caption render failed for '{chunk_text}': {e}")

    return caption_clips


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER: Auto Thumbnail
# ══════════════════════════════════════════════════════════════════════════════
def generate_thumbnail(video_clip, title_text, output_path):
    """
    Grab a frame from the video, overlay bold title text, save as JPG.
    Called automatically after video render.
    """
    try:
        # Grab frame at 1 second mark (usually a good representative frame)
        frame_time = min(1.0, video_clip.duration * 0.1)
        frame = video_clip.get_frame(frame_time)   # numpy array (H, W, 3)

        img = Image.fromarray(frame).resize((TARGET_WIDTH, TARGET_HEIGHT))

        # Dark gradient overlay at bottom for text readability
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        for y in range(TARGET_HEIGHT // 2, TARGET_HEIGHT):
            alpha = int(180 * (y - TARGET_HEIGHT // 2) / (TARGET_HEIGHT // 2))
            draw_ov.line([(0, y), (TARGET_WIDTH, y)], fill=(0, 0, 0, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        # Draw title text
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        except Exception:
            font = ImageFont.load_default()

        # Word-wrap manually
        words      = title_text.split()
        lines, cur = [], []
        for w in words:
            test = " ".join(cur + [w])
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > TARGET_WIDTH - 80:
                if cur:
                    lines.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(" ".join(cur))

        line_h  = 85
        total_h = len(lines) * line_h
        y_start = TARGET_HEIGHT - total_h - 80

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            x    = (TARGET_WIDTH - (bbox[2] - bbox[0])) // 2
            # Shadow
            draw.text((x + 3, y_start + 3), line, font=font, fill=(0, 0, 0))
            # Main text (yellow)
            draw.text((x, y_start), line, font=font, fill=(255, 230, 0))
            y_start += line_h

        thumb_path = output_path.replace(".mp4", "_thumbnail.jpg")
        img.save(thumb_path, "JPEG", quality=95)
        logger.info(f"✅ Thumbnail saved: {thumb_path}")
        return thumb_path

    except Exception as e:
        logger.error(f"Thumbnail generation failed: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════════════
def compile_final_video(video_clips_paths, voiceover_data, bgm_file_path, output_path,
                        title_text="Watch Till End"):
    """
    Compile final video with:
    - Duration 35–55 seconds  (auto-trimmed)
    - Fast cuts (2s per clip)
    - Clips matched to voiceover timing
    - Green/Yellow captions, 3 words at a time, top/center/bottom random position
    - Auto thumbnail generated
    - Background music at low volume
    """
    logger.info("🎬 Starting video compilation...")

    # ── 1. Load Voiceover ─────────────────────────────────────────────────────
    voice_clip = AudioFileClip(voiceover_data["audio_path"])
    raw_duration = voice_clip.duration

    # ── 2. Clamp duration to 35–55 s ─────────────────────────────────────────
    if raw_duration < MIN_DURATION:
        logger.warning(f"⚠️  Voiceover too short ({raw_duration:.1f}s). Padding to {MIN_DURATION}s.")
        duration = MIN_DURATION
    elif raw_duration > MAX_DURATION:
        logger.warning(f"⚠️  Voiceover too long ({raw_duration:.1f}s). Trimming to {MAX_DURATION}s.")
        voice_clip = voice_clip.subclip(0, MAX_DURATION)
        duration = MAX_DURATION
    else:
        duration = raw_duration

    logger.info(f"⏱  Final duration: {duration:.1f}s")

    # ── 3. Background Music ───────────────────────────────────────────────────
    audio_tracks = [voice_clip]
    if bgm_file_path and os.path.exists(bgm_file_path):
        try:
            bgm_raw  = AudioFileClip(bgm_file_path)
            bgm_clip = audio_loop(bgm_raw, duration=duration).volumex(0.06)
            audio_tracks.append(bgm_clip)
        except Exception as e:
            logger.warning(f"BGM load failed: {e}")

    final_audio = CompositeAudioClip(audio_tracks)

    # ── 4. Video Clips — Fast Cuts ────────────────────────────────────────────
    processed_clips = []
    available_clips = list(video_clips_paths)
    random.shuffle(available_clips)

    total_video_dur = 0.0

    # Diagnostics: log what we received
    logger.info(f"📂 Total clips received from media_fetcher: {len(available_clips)}")
    for i, p in enumerate(available_clips):
        exists = os.path.exists(p)
        size   = os.path.getsize(p) // 1024 if exists else 0
        logger.info(f"   [{i+1}] {p} | exists={exists} | size={size}KB")

    failed_clips = []

    for path in available_clips:
        if total_video_dur >= duration:
            break

        # BUG FIX: File existence + size check before VideoFileClip —
        # corrupt or 0-byte files cause cryptic ffmpeg errors
        if not os.path.exists(path):
            logger.warning(f"Skipping missing file: {path}")
            failed_clips.append((path, "file not found"))
            continue
        if os.path.getsize(path) < 10_000:
            logger.warning(f"Skipping too-small file ({os.path.getsize(path)} bytes): {path}")
            failed_clips.append((path, "file too small"))
            continue

        try:
            clip = VideoFileClip(path).without_audio()

            # BUG FIX: clip.duration < FAST_CUT_DUR check —
            # very short clips (< 1s) cause subclip errors
            if clip.duration < 1.0:
                logger.warning(f"Skipping clip too short ({clip.duration:.2f}s): {path}")
                clip.close()
                failed_clips.append((path, f"too short: {clip.duration:.2f}s"))
                continue

            # Resize & crop to vertical 9:16
            clip = clip.resize(height=TARGET_HEIGHT)
            if clip.w < TARGET_WIDTH:
                clip = clip.resize(width=TARGET_WIDTH)
            clip = clip.crop(
                x_center=clip.w / 2,
                width=TARGET_WIDTH,
                height=TARGET_HEIGHT
            )

            # Slight zoom-in (ken burns effect)
            clip = clip.fx(vfx.resize, lambda t: 1.0 + 0.03 * t)

            remaining = duration - total_video_dur
            cut_dur   = min(FAST_CUT_DUR, remaining, clip.duration)
            clip      = clip.subclip(0, cut_dur).set_duration(cut_dur)

            processed_clips.append(clip)
            total_video_dur += cut_dur
            logger.info(f"✅ Clip added: {os.path.basename(path)} ({cut_dur:.1f}s) | total={total_video_dur:.1f}s")

        except Exception as e:
            logger.error(f"Clip processing failed ({os.path.basename(path)}): {e}")
            failed_clips.append((path, str(e)))

    if failed_clips:
        logger.warning(f"⚠️  {len(failed_clips)} clip(s) failed:")
        for p, reason in failed_clips:
            logger.warning(f"   ✗ {os.path.basename(p)}: {reason}")

    if not processed_clips:
        # Detailed error to help diagnose root cause
        raise RuntimeError(
            f"No video clips could be processed.\n"
            f"  Clips received:  {len(available_clips)}\n"
            f"  Clips failed:    {len(failed_clips)}\n"
            f"  Failure reasons: {set(r for _, r in failed_clips)}\n"
            f"  Check: API keys in GitHub Secrets, DOWNLOADS_DIR in config.py, "
            f"network access to Pexels/Pixabay."
        )

    # ── 5. Concatenate clips ─────────────────────────────────────────────────
    final_video_concat = concatenate_videoclips(processed_clips, method="compose")

    # Ensure video length exactly matches audio duration
    if final_video_concat.duration < duration:
        # Loop last clip to fill remaining time
        last = processed_clips[-1]
        fill_dur = duration - final_video_concat.duration
        filler   = last.subclip(0, min(fill_dur, last.duration)).set_duration(fill_dur)
        processed_clips.append(filler)
        final_video_concat = concatenate_videoclips(processed_clips, method="compose")

    final_video_concat = final_video_concat.subclip(0, duration)

    # ── 6. Captions ──────────────────────────────────────────────────────────
    caption_clips = _build_caption_clips(voiceover_data, duration)
    logger.info(f"📝 Generated {len(caption_clips)} caption chunks")

    # ── 7. Composite ─────────────────────────────────────────────────────────
    layers = [final_video_concat] + caption_clips
    final_composite = CompositeVideoClip(layers, size=(TARGET_WIDTH, TARGET_HEIGHT))
    final_composite = final_composite.set_audio(final_audio).set_duration(duration)

    # ── 8. Render ─────────────────────────────────────────────────────────────
    logger.info(f"🚀 Rendering → {output_path}")
    final_composite.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        logger=None,   # suppress moviepy's own progress bar spam
    )

    # ── 9. Auto Thumbnail ─────────────────────────────────────────────────────
    thumb = generate_thumbnail(final_video_concat, title_text, output_path)
    if thumb:
        logger.info(f"🖼  Thumbnail: {thumb}")

    # ── 10. Cleanup ───────────────────────────────────────────────────────────
    final_composite.close()
    final_video_concat.close()
    voice_clip.close()
    for c in processed_clips:
        try:
            c.close()
        except Exception:
            pass

    logger.info("✅ Video compilation complete!")
    return output_path, thumb
