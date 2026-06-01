"""
script_generator.py — Groq LLM Script Engine (VIRAL SHORT-FORM v3.0 FIXED)
AI Dark Realities · YouTube Automation Pipeline
"""

import os
import json
import logging
import random
from groq import Groq
import config

logger = logging.getLogger(__name__)

# ---------------------------
# Fallback Topics
# ---------------------------
FALLBACK_TOPICS = [
    "The psychological experiment so disturbing it was banned",
    "Why your brain trusts strangers in seconds",
    "The dark reason people suddenly lose interest",
    "How manipulators control conversations without speaking",
    "The hidden signal liars accidentally reveal",
    "Why some people instantly feel familiar",
    "The psychology behind recurring nightmares",
    "How narcissists identify empathetic people",
    "The mystery behind hearing your name when alone",
    "Why silence makes some people uncomfortable",
    "The strange science behind deja vu",
    "The psychological weapon used by master manipulators",
    "What your brain notices before you do",
    "Why toxic relationships become addictive",
    "The dark psychology behind fake kindness",
    "The unsettling truth about intuition",
    "How your subconscious predicts outcomes",
    "The mystery psychologists still can't explain",
    "Why fear spreads faster than facts",
    "The hidden reason people sabotage themselves"
]


# ---------------------------
# Main Function
# ---------------------------
def generate_script(topic: str | None = None) -> dict:
    """
    Generate viral YouTube Shorts script using Groq API
    """

    logger.info("Starting Groq Script Engine...")

    api_key = os.getenv("GROQ_API_KEY") or getattr(config, "GROQ_API_KEY", None)
    if not api_key:
        raise ValueError("GROQ_API_KEY missing!")

    client = Groq(api_key=api_key)

    if not topic:
        topic = random.choice(FALLBACK_TOPICS)
        logger.info(f"Random topic selected: {topic}")
    else:
        logger.info(f"Topic received: {topic}")

    # ---------------------------
    # System Prompt
    # ---------------------------
    system_instruction = (
        "You are a viral YouTube Shorts script writer.\n"
        "Niche: Psychology, Mystery, Human Behavior.\n\n"

        "RULES:\n"
        "1. 90-130 words script.\n"
        "2. Start with strong mystery hook.\n"
        "3. Must include suspense + curiosity gaps.\n"
        "4. Never reveal everything early.\n"
        "5. Use cinematic tone.\n"
        "6. Include EXACTLY ONE: 'Wait for it...' or 'But here's the twist...'\n"
        "7. End with CTA (Follow / Comment / Save).\n"
        "8. No violence, no harmful content.\n\n"

        "Return ONLY JSON:\n"
        "{"
        '"hook":"",'
        '"script":"",'
        '"seo":{"title":"","description":""},'
        '"broll_keywords":[]'
        "}"
    )

    user_prompt = f"Topic: {topic}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.95,
            top_p=0.95,
            response_format={"type": "json_object"}
        )

        script_data = json.loads(completion.choices[0].message.content)

        # ---------------------------
        # Validation Safety Layer
        # ---------------------------
        if not isinstance(script_data.get("broll_keywords"), list):
            script_data["broll_keywords"] = [
                "dark psychology",
                "brain mystery",
                "human behavior",
                "cinematic shadow",
                "neural glow"
            ]

        if "hook" not in script_data:
            script_data["hook"] = "Your brain is hiding something from you."

        if "script" not in script_data:
            script_data["script"] = (
                "Your brain notices things before you do. "
                "Most people never realize this hidden pattern. "
                "Wait for it... "
                "Your subconscious reacts first, your mind follows later. "
                "Comment if you noticed this."
            )

        if "seo" not in script_data:
            script_data["seo"] = {
                "title": "Brain Secret 🧠",
                "description": "#darkpsychology #mindhacks #psychologyfacts"
            }

        return script_data

    except Exception as e:
        logger.error(f"Script generation failed: {e}")

        return {
            "hook": "Your brain already knows this secret.",
            "script": (
                "Your brain detects patterns before you notice them. "
                "Most people ignore this hidden signal. "
                "Wait for it... "
                "Your subconscious reacts faster than your thoughts. "
                "Comment if this surprised you."
            ),
            "seo": {
                "title": "Brain Secret 🧠",
                "description": "#darkpsychology #mindhacks #psychologyfacts"
            },
            "broll_keywords": [
                "dark psychology",
                "brain mystery",
                "human behavior",
                "cinematic shadow",
                "neural glow"
            ]
        }
