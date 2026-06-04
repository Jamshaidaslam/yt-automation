"""
script_generator.py — Core Intelligence Engine (GROQ LLAMA3.3-70B BLUEPRINT v3.3 - MODEL FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fixed: Replaced decommissioned Llama3-70b with the latest supported Llama-3.3-70b-versatile API model.
───────────────────────────────────────────────────────────────────────────────────
"""

import json
import os
import re
import logging
from groq import Groq

logger = logging.getLogger(__name__)

def generate_script(topic: str) -> dict:
    """Generates an elite psychological script with strict high-retention aesthetic video anchors."""
    logger.info(f"🧠 Generating deep psychological narrative blueprint for topic: [{topic}]")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable assignment.")

    client = Groq(api_key=api_key)

    # Array structure mapping to bypass Python's native multi-line literal parser limits
    prompt_lines = [
        "You are an elite content strategist specializing in dark psychology, human behaviors, and viral mystery shorts for USA/UK audiences.",
        "Your writing is cinematic, suspenseful, and hypnotic.",
        "STRICT OUTPUT FORMAT:",
        "You must return ONLY a raw JSON object. Do not include markdown blocks, do not write any introductory or concluding prose.",
        "JSON STRUCTURE:",
        "{",
        "  \"title\": \"A high-CTR clickbait title optimized for automated loop tracking\",",
        "  \"voiceover\": \"The full text script to be spoken. MUST include the word 'WAIT' naturally as a mid-video cliffhanger pause.\",",
        "  \"scenes\": [",
        "    {",
        "      \"text_segment\": \"Exact short phrase matching the voiceover progression\",",
        "      \"visual_query\": \"STRICT SEARCH TERMS. Use only terms like: dark psychology silhouette, subconscious mind aesthetic, mysterious glitch art, brain hacking visual, moody cinematic shadow, creepy psychological macro clip.\"",
        "    }",
        "  ]",
        "}"
    ]
    system_prompt = "\n\n".join(prompt_lines)

    user_prompt = f"Create a chilling, highly educational short-form script about: {topic if topic else 'Dark Psychology'}. Ensure the final loop sentence connects back smoothly to the beginning hook line."

    # 🔥 FIX: Deployed the latest upgraded Llama-3.3-70b model to fix decommissioning error
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.65,
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

    logger.info("✅ Script successfully compiled and contextualized using Llama-3.3.")
    return data
