"""
script_generator.py — Groq LLM Script Engine (VIRAL SHORT-FORM v3.1 FIXED)
AI Dark Realities · YouTube Automation Pipeline
Optimized for USA audience + 40-55 sec shorts
"""

import os
import json
import logging
import random
from groq import Groq
import config

logger = logging.getLogger(__name__)

# ---------------------------
# Fallback Topics - USA Viral Topics
# ---------------------------
FALLBACK_TOPICS = [
    "Why your brain trusts strangers in 7 seconds",
    "The dark psychology trick casinos use on you",
    "How manipulators control conversations without speaking",
    "The hidden signal liars accidentally reveal",
    "Why silence makes powerful people uncomfortable",
    "The psychology behind recurring nightmares",
    "How narcissists instantly spot empathetic people",
    "Why your brain hears your name when alone",
    "The strange science behind deja vu",
    "The psychological weapon used by master manipulators",
    "What your brain notices before you do",
    "Why toxic relationships become addictive",
    "The dark psychology behind fake kindness",
    "How your subconscious predicts the future",
    "Why fear spreads faster than facts on social media",
    "The hidden reason people sabotage their own success",
    "Why you procrastinate even when you know better",
    "The psychology of why you can't stop scrolling",
    "How your brain creates fake memories",
    "The dark reason people ghost you suddenly"
]

# ---------------------------
# Main Function
# ---------------------------
def generate_script(topic: str | None = None) -> dict:
    """
    Generate viral YouTube Shorts script using Groq API
    Optimized for 40-55 sec + USA retention
    """

    logger.info("Starting Groq Script Engine v3.1...")

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
    # System Prompt - FIXED FOR VIRAL + USA
    # ---------------------------
    system_instruction = (
        "You are a viral YouTube Shorts script writer for USA audience.\n"
        "Niche: Dark Psychology & Mind Tricks.\n\n"
        "RULES:\n"
        "1. 65-85 words script. Max 85 words for 40-55 sec video.\n"
        "2. First 3 words MUST be: You / Your brain / Stop scrolling / 90% people / Never do this\n"
        "3. Must include suspense + curiosity gaps. Never reveal everything early.\n"
        "4. Add... after every 7-8 words for dramatic pause effect\n"
        "5. Include EXACTLY ONE: 'Wait for it...' or 'But here's the twist...'\n"
        "6. End with CTA: Follow for part 2 / Save this / Comment which one shocked you\n"
        "7. Banned words: kill, suicide, murder, blood, death. Use 'dark trick', 'mind hack', 'psychology trap' instead\n"
        "8. Title must be 5 words max + 1 emoji. Ex: Your Brain Lies 🧠\n"
        "9. Tone: Direct, dark, like a smart friend warning you. Use 'you' 5+ times.\n\n"
        "Return ONLY JSON:\n"
        '{"hook":"",'
        '"script":"",'
        '"seo":{"title":"","description":""},'
        '"broll_keywords":[]'
        "}"
    )

    user_prompt = f"Topic: {topic}. Write for USA audience aged 18-35."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8, # FIXED: 0.95 se 0.8 kiya for consistency
            top_p=0.9,
            response_format={"type": "json_object"}
        )

        script_data = json.loads(completion.choices[0].message.content)

        # ---------------------------
        # Validation Safety Layer - FIXED
        # ---------------------------
        if not isinstance(script_data.get("broll_keywords"), list) or len(script_data["broll_keywords"]) < 3:
            script_data["broll_keywords"] = [
                "brain scan",
                "eye closeup",
                "shadow figure",
                "neon brain",
                "psychology test"
            ]

        if "hook" not in script_data or len(script_data["hook"].split()) < 3:
            script_data["hook"] = "Your brain is hiding this from you."

        if "script" not in script_data:
            script_data["script"] = (
                "Your brain... notices things before you do... "
                "Most people... never realize this hidden pattern... "
                "Wait for it... "
                "Your subconscious... reacts first, your mind follows later... "
                "Comment if this shocked you..."
            )

        if "seo" not in script_data:
            script_data["seo"] = {
                "title": "Brain Secret 🧠",
                "description": "#darkpsychology #mindhacks #psychologyfacts"
            }

        # Word count check for 40-55 sec
        word_count = len(script_data["script"].split())
        if word_count > 85:
            logger.warning(f"Script too long: {word_count} words. Truncating...")
            words = script_data["script"].split()[:85]
            script_data["script"] = " ".join(words) + "..."

        logger.info(f"Script generated: {word_count} words")
        return script_data

    except Exception as e:
        logger.error(f"Script generation failed: {e}")

        return {
            "hook": "Your brain already knows this secret.",
            "script": (
                "Your brain... detects patterns before you notice them... "
                "Most people... ignore this hidden signal... "
                "Wait for it... "
                "Your subconscious... reacts faster than your thoughts... "
                "Comment if this surprised you..."
            ),
            "seo": {
                "title": "Brain Secret 🧠",
                "description": "#darkpsychology #mindhacks #psychologyfacts"
            },
            "broll_keywords": [
                "brain scan",
                "eye closeup",
                "shadow figure",
                "neon brain",
                "psychology test"
            ]
        }
