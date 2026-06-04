"""
script_generator.py — Core Intelligence Engine (GROQ LLAMA3-70B DEEP DARK BLUEPRINT v3.1 - SYNTAX FIXED)
AI Dark Realities · Short-Form Video Pipeline
Fixed: Escape and raw string containment to resolve unterminated string literal errors.
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

    # Elite psychological system prompt focusing strictly on high-retention dark hooks and viral loops
    system_prompt = (
        "You are an elite content strategist specializing in dark psychology, human behaviors, and viral mystery shorts "
        "for USA/UK audiences. Your writing is cinematic, suspenseful, and hypnotic.\n\n"
        "STRICT OUTPUT FORMAT:\n"
        "You must return ONLY a raw JSON object. Do not include markdown code blocks, do not write any introductory or concluding prose.\n\n"
        "JSON STRUCTURE:\n"
        "{\n"
        "  \"title\": \"A high-CTR clickbait title optimized for automated loop tracking\",\n"
        "  \"voiceover\": \"The full text script to be spoken. MUST include the word 'WAIT' naturally as a mid-video dramatic cliffhanger pause block.\",\n"
        "  \"scenes\": [\n"
        "    {\n"
        "      \"text_segment\": \"Exact short phrase matching the voiceover progression\",\n"
        "      \"visual_query\": \"STRICT SEARCH TERMS. Use only terms like: 'dark psychology silhouette', 'subconscious mind aesthetic', 'mysterious glitch art', 'brain hacking visual', 'moody cinematic shadow', 'creepy psychological macro clip'. Avoid generic terms like coffee or corporate traffic.\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    user_prompt = f"Create a chilling, highly educational short-form script about: {topic if topic else 'Dark Psychology'}. Ensure the final loop sentence connects back smoothly to the beginning hook line."

    response = client.chat.completions.create(
        model="llama3-70b-8192",
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

    logger.info("✅ Script successfully compiled and contextualized.")
    return data
