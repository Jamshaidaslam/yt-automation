"""
script_generator.py — Ultimate Viral Dark Psychology Engine
AI Dark Realities · USA/UK Viral Shorts Generator (FAST CUTS CONFIG)
───────────────────────────────────────────────────────────────────────────────────
"""
import json
import os
import re
import logging
from groq import Groq

logger = logging.getLogger(__name__)

def generate_script(topic: str) -> dict:
    logger.info(f"🧠 Generating fast-paced dark psychology script for topic: [{topic}]")
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable.")

    client = Groq(api_key=api_key)

    prompt_lines = [
        "You are a world-class viral content architect specializing in Dark Psychology and high-retention short-form videos.",
        "Your mission is to engineer a highly addictive script with dramatic pacing.",
        
        "VOICEOVER & NATURAL PACING REQUIREMENTS:",
        "- MUST contain between 90 and 120 words total.",
        "- Use frequent commas (,) and punctuation marks. This forces the TTS engine to take natural human breaths and avoid sounding robotic.",
        "- End with a continuous loop sentence that perfectly feeds back into the first hook sentence.",

        "FAST CUTS & SCENE REQUIREMENTS:",
        "- Generate EXACTLY 12 small chronological scenes. This ensures a fast cut every 2 to 3 seconds.",
        "- Each scene must have a very short, hyper-focused portrait visual query for Pexels.",

        "STRICT OUTPUT FORMAT:",
        "- Return ONLY a valid JSON object. No markdown syntax or explanations.",

        "JSON STRUCTURE INTERFACE:",
        "{",
        '  "title": "High CTR viral title",',
        '  "voiceover": "The entire 90-120 words continuous narrative with punctuation marks for deep natural pauses.",',
        '  "scenes": [',
        '    {"scene_number": 1, "visual_query": "dark silhouette face shadow"},',
        '    {"scene_number": 2, "visual_query": "smartphone screen glow dark room"},',
        '    {"scene_number": 3, "visual_query": "anxious person hands typing"},',
        '    {"scene_number": 4, "visual_query": "macro human eye dilating"},',
        '    {"scene_number": 5, "visual_query": "mysterious concrete alleyway dark"},',
        '    {"scene_number": 6, "visual_query": "abstract digital matrix code"},',
        '    {"scene_number": 7, "visual_query": "person head in hands stressed"},',
        '    {"scene_number": 8, "visual_query": "security camera red blinking light"},',
        '    {"scene_number": 9, "visual_query": "silhouette walking away fog"},',
        '    {"scene_number": 10, "visual_query": "close up phone screen scrolling"},',
        '    {"scene_number": 11, "visual_query": "moody neon rain reflection"},',
        '    {"scene_number": 12, "visual_query": "dark psychological realization portrait"}',
        '  ]',
        "}"
    ]

    system_prompt = "\n".join(prompt_lines)
    user_prompt = f"Create a high-retention 12-scene dark psychology loop script about: {topic if topic else 'Dark Psychology'}. Ensure the voiceover has 90-120 words with deep dramatic punctuation."

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.75,
        max_tokens=1500,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw_output = response.choices[0].message.content.strip()
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if not match:
            raise RuntimeError(f"Could not parse JSON: {raw_output}")
        data = json.loads(match.group(0))

    return data
