"""
script_generator.py — Core Intelligence Engine (GROQ LLAMA3.3-70B HYPNOTIC LOOP v4.5)
AI Dark Realities · Short-Form Video Pipeline
Upgraded for: USA/UK Premium Audience, 2-Second Mystery Vibe Silence, and Flawless Loopback
───────────────────────────────────────────────────────────────────────────────────
"""

import json
import os
import re
import logging
from groq import Groq

logger = logging.getLogger(__name__)

def generate_script(topic: str) -> dict:
    """
    Generates a dark psychology script with a mandatory 2-second suspense pause 
    immediately after the viral hook, moving directly into body data and an infinite loop.
    """
    logger.info(f"🧠 Engineering viral hypnotic loop blueprint for topic: [{topic}]")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable assignment.")

    client = Groq(api_key=api_key)

    prompt_lines = [
        "You are the world's most dangerous viral short-form director specializing in hypnotic dark psychology content for USA/UK audiences.",
        
        "STRICT SCRIPT STRUCTURAL MATRIX (FOLLOW EXACTLY):",
        "1. THE 2-SECOND SHOCKING HOOK: The first sentence must be an extreme psychological hook (4-6 words maximum). It must strike fear, status, or hidden control instantly. Do not say conversational fillers.",
        
        "2. THE MANDATORY SUSPENSE GAP (MYSTERY VIBE): Immediately after the very first sentence, you MUST insert a dedicated scene where the voiceover text is exactly '... WAIT. ...'. This triggers a 2-second absolute silence from the narrator while the dark music and room noise create a chilling suspense vibe on screen.",
        
        "3. THE BODY CONTENT: Keep sentences ultra-short (4-5 words max per scene block) using premium workplace manipulation, high-status body language, or social engineering topics.",
        
        "4. THE GRAMMATICAL LOOPBACK: The final sentence of the script must structurally, grammatically, and seamlessly flow directly back into the very first hook sentence without any logical gap, making it a 100% endless infinite loop.",
        
        "5. SPECIFIC VISUAL QUERIES: Provide elite cinematic keywords for Pexels that match dark psychology (e.g., 'mysterious shadow close up', 'psychological macro glitch', 'moody corporate mastermind silhouette').",

        "STRICT OUTPUT FORMAT:",
        "Return ONLY a valid, raw JSON object. Do not include markdown wraps (like ```json), introduction prose, or trailing notes.",
        
        "JSON EXPECTED LAYOUT STRUCTURE:",
        "{",
        "  \"title\": \"Extreme high-CTR clickbait title optimized for loops\",",
        "  \"voiceover\": \"The full combined script text including the hook, the words '... WAIT. ...', the body, and the loopback tail.\",",
        "  \"scenes\": [",
        "    {",
        "      \"text_segment\": \"The First Viral Hook Sentence Here\",",
        "      \"visual_query\": \"intense psychological macro eye contact, dark moody silhouette\" ",
        "    },",
        "    {",
        "      \"text_segment\": \"... WAIT. ...\",",
        "      \"visual_query\": \"mysterious smoke floating shadow, cinematic dark static glitch\"",
        "      \"note\": \"This forces the automated engine to render 2 seconds of pure ambient mystery vibe background sound without voiceover.\"",
        "    },",
        "    {",
        "      \"text_segment\": \"First sentence of body content here\",",
        "      \"visual_query\": \"dark concrete corporate architecture moody close up\"",
        "    }",
        "    # Continue linear progression until the loopback sentence...",
        "  ]",
        "}"
    ]
    system_prompt = "\n\n".join(prompt_lines)

    fallback_topic = "Uncomfortable dark manipulation tricks used in high-status boardrooms and public spaces"
    active_topic = topic.strip() if topic and topic.strip() else fallback_topic

    user_prompt = (
        f"Create a chilling, highly professional USA/UK target short script about: '{active_topic}'.\n"
        f"Enforce the Matrix: Scene 1 is the lethal hook. Scene 2 is strictly text_segment '... WAIT. ...' for the mystery vibe silence. "
        f"The subsequent scenes are short factual body steps, and the very last scene loops flawlessly back into Scene 1."
    )

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
            raise RuntimeError("Groq model output corrupted outside expected JSON boundaries.")

    logger.info("✅ Hypnotic Loop Script Blueprint compiled using Llama-3.3.")
    return data
