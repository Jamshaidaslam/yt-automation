"""
script_generator.py — Core Intelligence Engine (GROQ LLAMA3.3-70B HYPNOTIC LOOP v4.6)
Updated: Clean JSON Enforcement & Structural Logic for 1M+ Retention
"""

import json
import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

def generate_script(topic: str) -> dict:
    logger.info(f"🧠 Engineering viral hypnotic loop blueprint for: [{topic}]")
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    system_prompt = """
    You are an elite director of dark psychology content for USA/UK audiences.
    
    STRICT STRUCTURE:
    1. Hook: 4-6 words max. Lethal status/control/fear.
    2. Silence Scene: Scene 2 must strictly be text_segment "... WAIT. ..." with 2s silence.
    3. Body: Short punchy facts (4-5 words per scene).
    4. Loopback: Final sentence must flow directly into the Hook.
    
    OUTPUT: Return ONLY a raw JSON object (no markdown, no backticks).
    
    SCHEMA:
    {
      "title": "Viral CTR Title",
      "voiceover": "Full script text...",
      "scenes": [
        {"text_segment": "...", "visual_query": "..."},
        {"text_segment": "... WAIT. ...", "visual_query": "..."}
      ]
    }
    """

    user_prompt = f"Topic: {topic}. Create the viral loop script now."

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6,
        response_format={"type": "json_object"}
    )

    try:
        # Extra safety: Strip potential markdown if model ignores instruction
        content = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        return data
    except Exception as e:
        logger.error(f"Script Generation Failed: {e}")
        raise
