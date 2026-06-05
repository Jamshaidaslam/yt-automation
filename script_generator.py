"""
script_generator.py — Core Intelligence Engine (GROQ LLAMA3.3-70B - LONG SHORT CONFIG)
AI Dark Realities · Short-Form Video Pipeline
───────────────────────────────────────────────────────────────────────────────────
"""

import json
import os
import re
import logging
from groq import Groq

logger = logging.getLogger(__name__)

def generate_script(topic: str) -> dict:
    logger.info(f"🧠 Generating deep psychological narrative blueprint for topic: [{topic}]")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable assignment.")

    client = Groq(api_key=api_key)

    # Strict system prompt to enforce 35-55 seconds video script length
    prompt_lines = [
        "You are an elite content strategist specializing in dark psychology and viral mystery shorts for USA/UK audiences.",
        "Your writing style is highly cinematic, intense, suspenseful, and hypnotic.",
        "CRITICAL REQUIREMENT FOR LENGTH:",
        "The video MUST be between 35 to 55 seconds long. To achieve this, the 'voiceover' field MUST contain exactly between 90 to 130 words.",
        "Do not write a short 20-word summary. Give a deep, fully completed psychological concept with a strong psychological hook, an elaborate dark explanation, and a mind-blowing realization.",
        "Provide exactly 4 to 5 distinct chronological scenes to perfectly map this longer script duration.",
        "STRICT OUTPUT FORMAT:",
        "You must return ONLY a raw JSON object. Do not include markdown blocks like ```json, do not write any introductory or concluding prose.",
        "JSON STRUCTURE:",
        "{",
        "  \"title\": \"A high-CTR clickbait title optimized for loop tracking\",",
        "  \"voiceover\": \"The entire 90-130 words voiceover narrative script without any scene tags or speaker names. Smoothly connected for narration.\",",
        "  \"scenes\": [",
        "    {",
        "      \"scene_number\": 1,",
        "      \"visual_query\": \"STRICT PEXELS SEARCH TERMS. Use only specific portrait keywords like: dark psychology silhouette, moody cinematic shadow, phone screen glow in dark, brain hacking visual.\"",
        "    }",
        "  ]",
        "}"
    ]
    system_prompt = "\n\n".join(prompt_lines)

    user_prompt = f"Write a complete, high-retention 35-55 seconds psychological thriller script about: {topic if topic else 'Dark Psychology'}. Ensure the voiceover is detailed, explains the entire dynamic concept, has 90-130 words, and ends with a viral loop sentence that seamlessly connects back to the very first hook sentence."

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    raw_json = response.choices[0].message.content.strip()
    
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw_json, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            raise RuntimeError("Groq pipeline output could not be formatted into proper JSON context.")

    # Validation check to ensure voiceover is not empty or too small
    word_count = len(data.get("voiceover", "").split())
    logger.info(f"✅ Script ready — {word_count} words generated for a complete 35-55s concept.")
    
    return data
