"""
script_generator.py — Groq LLM Script Engineering Engine (VIRAL SHORT-FORM RULES v2.8)
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import os
import json
import logging
import random
from groq import Groq
import config

logger = logging.getLogger(__name__)

# Fallback topics agar main pipeline mein topic pass na ho
FALLBACK_TOPICS = [
    "How to detect if someone is lying instantly",
    "The dark psychology of silent treatment",
    "How to make someone think about you constantly",
    "A psychological trick to gain instant respect",
    "The mirror hack to read anyone's hidden thoughts"
]


def generate_script(topic: str | None = None) -> dict:
    """
    Groq API ko call karta hai strict viral guidelines ke sath 
    aur Structured JSON response return karta hai.
    """
    logger.info("Initializing Groq AI script writer framework...")
    
    api_key = os.getenv("GROQ_API_KEY") or getattr(config, "GROQ_API_KEY", None)
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing!")

    client = Groq(api_key=api_key)

    if not topic:
        topic = random.choice(FALLBACK_TOPICS)
        logger.info(f"No specific topic forced. Selected viral fallback: '{topic}'")
    else:
        logger.info(f"Generating high-retention script for forced topic: '{topic}'")

    # 🔥 VIRAL SYSTEM PROMPT WITH YOUR EXACT RULES
    system_instruction = (
        "You are a viral YouTube Shorts script writer for USA audience. Niche: Dark Psychology & Mind Tricks.\n\n"
        "Rules - Lazmi follow karo:\n"
        "1. Length: 40-55 seconds when spoken. Max 85 words.\n"
        "2. First 3 words MUST be one of these exact phrases: 'You', 'Your brain', 'Stop scrolling', '90% people', 'Never do this'. Choose the most fitting one.\n"
        "3. Tone: Direct, dark, slightly threatening but not banned. Like a smart friend warning you.\n"
        "4. Structure:\n"
        "   Hook: 1 line - curiosity gap\n"
        "   Body: 2-3 mind tricks/facts. Each fact 1 sentence only.\n"
        "   Pause: Add '...' after every 7-8 words for dramatic effect\n"
        "   CTA: Last line = 'Follow for part 2' OR 'Save this before you forget' OR 'Comment which one shocked you'\n"
        "5. Words banned: kill, suicide, murder, blood. Use 'dark trick', 'mind hack', 'psychology' instead.\n"
        "6. Make it sound human, not Wikipedia. Use the word 'you' at least 5+ times.\n"
        "7. Add exactly 1 'pattern interrupt' in the middle: 'Wait for it...' OR 'But here's the twist...'\n\n"
        "CRITICAL: You MUST respond ONLY with a raw JSON object. Do not include any intro, outro, markdown, or chat text outside the JSON. "
        "The JSON must have these exact keys:\n"
        '{\n'
        '  "hook": "The single hook sentence.",\n'
        '  "script": "The full voiceover script containing max 85 words with ... dramatic pauses.",\n'
        '  "seo": {\n'
        '    "title": "A 5 words max title with an emoji.",\n'
        '    "description": "Short dark description with hashtags: #darkpsychology #mindhacks #psychologyfacts"\n'
        '  },\n'
        '  "broll_keywords": ["keyword1", "keyword2", "keyword3"]\n'
        '}'
    )

    user_prompt = f"Topic: {topic}\n\nGenerate the complete JSON script now based on the forced rules."

    try:
        # LLM Completion Request
        completion = client.chat.completions.create(
            model="llama-3.3-70b-specdec", # Ultra-fast high quality logic model
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.75,
            response_format={"type": "json_object"} # Force valid JSON generation
        )

        raw_response = completion.choices[0].message.content
        script_data = json.loads(raw_response)
        
        logger.info("⚡ Groq script successfully generated and parsed into JSON structure.")
        
        # Validation checks to ensure keywords exist for video compiler
        if "broll_keywords" not in script_data or not script_data["broll_keywords"]:
            script_data["broll_keywords"] = ["dark psychology shadow", "manipulation brain glow", "mysterious silhouette"]
            
        return script_data

    except Exception as e:
        logger.error(f"Groq Script generation failed: {e}. Executing emergency hardcoded script.")
        # Fallback backup response in case API limit hits or crashes
        return {
            "hook": "Your brain is keeping a dark secret from you.",
            "script": "Your brain ... is keeping a dark secret ... from you. 90% of people ... fall into this trap every day. When someone stares ... at your lips ... they are thinking about manipulation. But here's the twist ... you can completely reverse the power. Stare back at their forehead ... to instantly break their focus. Save this before you forget.",
            "seo": {
                "title": "Brain Traps Exposed 🧠",
                "description": "Unlocking the secrets of hidden manipulation. #darkpsychology #mindhacks #psychologyfacts"
            },
            "broll_keywords": ["dark aesthetic brain", "mysterious eyes shadow", "glitch neon neural"]
        }
