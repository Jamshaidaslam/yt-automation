"""
script_generator.py — Core Intelligence Engine (GROQ LLAMA3.3-70B VIRAL ENGINE v4.0)
AI Dark Realities · Short-Form Video Pipeline
Upgraded for: USA/UK High-Volume Premium Audience (Low-Competition Corporate & Social Engineering)
Formula: 2-Second Freeze Hook + Strict Phrase Synchronization + Seamless Loop Architecture
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
    Generates an elite psychological script engineered for massive USA/UK audience retention.
    Automatically forces high-CTR angles, hypnotic sub-second hooks, and precise visual tagging.
    """
    logger.info(f"🧠 Engineering viral psychological narrative blueprint for topic: [{topic}]")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable assignment.")

    client = Groq(api_key=api_key)

    # 🚀 SYSTEM PROMPT: Engineered for 99th-percentile retention hooks & professional pacing
    prompt_lines = [
        "You are the world's elite viral content architect specializing in dark psychology, behavioral economics, and hidden human manipulation tactics.",
        "Your target audience is the USA and UK. They demand sharp, high-intellect, non-cringe, and deeply mysterious narratives.",
        
        "CRITICAL SCRIPTWRITING RULES:",
        "1. THE 2-SECOND FREEZE HOOK: The script must start with an aggressive, heart-stopping psychological hook. Do not say 'Welcome back' or 'In this video'. Start immediately with a shocking statement targeting the viewer's security, status, or autonomy (e.g., 'You are being silently evaluated right now...', 'The top 1% use a disturbing eye trick to control rooms...').",
        "2. HIGH-VOLUME TARGET NICHES: If the user provides a generic topic, twist the angle into one of these three high-retention categories: Workplace/Corporate Sabotage, High-Status Body Language Control, or Social Engineering/Digital Addiction Mechanics.",
        "3. WORD PACE & PHRASES: Write short, snappy sentences (maximum 4-6 words per segment) to allow fast visual cuts. Include the word 'WAIT.' as a dramatic, solitary mid-video cliffhanger pause.",
        "4. PERFECT INFULENCER LOOP: The final sentence must seamlessly and grammatically connect back to the very first hook sentence of the script, making the video a 100% infinite loop.",
        "5. EXACT VISUAL QUERIES: For each segment, provide 3 to 4 strict, high-quality search keywords for Pexels. Avoid generic terms. Use elite descriptors: 'dark corporate moody silhouette', 'intense eye contact macro', 'cyberpunk server glitch room', 'shadowy psychological mastermind', 'vintage concrete architecture moody close up'.",

        "STRICT OUTPUT FORMAT:",
        "You must return ONLY a raw JSON object. Do not include markdown wraps (like ```json), intro prose, or conversational filler.",
        
        "JSON STRUCTURE LAYOUT:",
        "{",
        "  \"title\": \"Extreme high-CTR clickbait title optimized for loops\",",
        "  \"voiceover\": \"The complete raw text script to be spoken, including the word 'WAIT.'\",",
        "  \"scenes\": [",
        "    {",
        "      \"text_segment\": \"Exact short word phrase (4-6 words max) progressing linearly through the voiceover\",",
        "      \"visual_query\": \"3-4 strict specific search keywords matching this precise emotional or psychological segment\"",
        "    }",
        "  ]",
        "}"
    ]
    system_prompt = "\n\n".join(prompt_lines)

    # Automatically engineer user prompt into an elite hook structure if it's empty
    fallback_topic = "Corporate psychological tactics used by toxic managers or hidden power dynamics in public rooms"
    active_topic = topic.strip() if topic and topic.strip() else fallback_topic

    user_prompt = (
        f"Generate a masterfully crafted, chilling, and highly educational dark psychology script about: '{active_topic}'.\n"
        f"Remember: First sentence must be a severe retention hook, sentences must be broken down into 4-6 word chunks in the scenes array, "
        f"and the final sentence must loop perfectly into the first hook phrase."
    )

    # Execution via Llama-3.3-70b-versatile
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.68,  # Slightly raised for more creative, eerie metaphors
        response_format={"type": "json_object"}
    )

    raw_json = response.choices[0].message.content.strip()
    
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        # Fallback regex parsing to catch loose strings
        match = re.search(r'\{.*\}', raw_json, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            raise RuntimeError("Groq output stream dropped out of acceptable JSON parameters.")

    logger.info("✅ Elite USA/UK Script successfully generated and structured.")
    return data
