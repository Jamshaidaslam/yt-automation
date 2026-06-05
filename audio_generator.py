"""
audio_generator.py — Production Voice Synthesis Layer (PRO ENGINE v3.5 - SSML PITCH & SUBMAKER SYNC)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
"""

import os
import re
import logging
import asyncio
from pathlib import Path
import edge_tts

logger = logging.getLogger(__name__)

def inject_dynamic_ssml(text_script: str, voice_id: str) -> str:
    """Wraps keywords in dramatic SSML tags to force automatic pitch drops and deep pauses."""
    words = text_script.split()
    processed_words = []
    
    # Intentionally slowing down standard speed for deep dramatic "thahrao"
    base_rate = "-6%" 
    base_pitch = "-3Hz"

    for word in words:
        clean = re.sub(r'[^\w]', '', word).upper()
        # High-retention shock keywords get custom deep scary pitch shifts
        if clean in ["TRAP", "CONTROL", "CONTROLS", "DARK", "MIND", "PSYCHOLOGY", "ADDICTION", "WARNING", "SECRET", "EXPLOITS", "ANXIETY", "STRESS"]:
            processed_words.append(f'<prosody pitch="-18Hz" rate="-15%">{word}</prosody>')
        elif clean in ["YOU", "YOUR", "PHONE", "TRACKING"]:
            processed_words.append(f'<prosody pitch="-10Hz" rate="-8%">{word}</prosody>')
        else:
            processed_words.append(word)

    scary_script = " ".join(processed_words)
    
    # Add deep breathing pauses at commas and periods
    scary_script = scary_script.replace(", ", ', <break time="450ms"/> ')
    scary_script = scary_script.replace(". ", '. <break time="750ms"/> ')

    ssml_payload = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="{voice_id}">
            <prosody rate="{base_rate}" pitch="{base_pitch}">
                {scary_script}
            </prosody>
        </voice>
    </speak>"""
    return ssml_payload

def generate_voiceover(text_script: str, output_filename: str, voice_type: str = "guy_dark") -> dict:
    logger.info("🎙️ Activating Native SSML Pitch Shift & Token Sync Engine...")
    
    output_dir = Path("output/media")
    output_dir.mkdir(parents=True, exist_ok=True)
    target_audio_path = output_dir / f"{output_filename}.mp3"

    if target_audio_path.exists():
        try: target_audio_path.unlink()
        except: pass

    voice_id = "en-US-ChristopherNeural" if voice_type == "guy_dark" else "en-US-GuyNeural"
    ssml_content = inject_dynamic_ssml(text_script, voice_id)
    
    word_timings = []

    async def _render_tts_with_sync():
        # Communicate using custom SSML instead of raw text for pitch controls
        communicate = edge_tts.Communicate(ssml_content, voice_id, is_ssml=True)
        submaker = edge_tts.SubMaker()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                with open(target_audio_path, "ab") as f:
                    f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # SubMaker automatically extracts exact milliseconds from the streaming voice
                submaker.feed(chunk)
                
        # Parse official SubMaker offset intervals back to seconds
        for offset, _, text in submaker.offset_and_text:
            start_sec = offset[0] / 10000000.0  # Convert edge-tts ticks to float seconds
            end_sec = offset[1] / 10000000.0
            word_timings.append({
                "word": text,
                "start": round(start_sec, 2),
                "end": round(end_sec, 2)
            })

    try:
        asyncio.run(_render_tts_with_sync())
    except Exception as tts_err:
        logger.error(f"❌ Custom SSML Sync Failed: {tts_err}")
        # Secure basic fallback if runner crashes
        communicate = edge_tts.Communicate(text_script, voice_id, rate="-5%", pitch="-3Hz")
        asyncio.run(communicate.save(target_audio_path))

    # Fallback timing parser if streaming submaker mapping is empty
    if not word_timings:
        current_time = 0.0
        for word in text_script.split():
            duration = 0.45 if len(word) > 5 else 0.32
            word_timings.append({"word": word, "start": current_time, "end": current_time + duration})
            current_time += duration + 0.05

    from moviepy.editor import AudioFileClip
    try: real_duration = AudioFileClip(str(target_audio_path)).duration
    except: real_duration = word_timings[-1]["end"] if word_timings else 30.0

    payload = {
        "audio_path": str(target_audio_path),
        "word_timings": word_timings,
        "duration": real_duration
    }
    logger.info(f"✅ Voice Sync Locked. Total synced words mapped: {len(word_timings)}")
    return payload
