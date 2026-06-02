"""
script_generator.py — Groq LLM Script Engine (VIRAL + HUMAN v3.2 FIXED)
AI Dark Realities · YouTube Automation Pipeline
Optimized for USA audience + 40-55 sec shorts + Human tone
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
    Optimized for 40-55 sec + USA retention + Human tone
    """

    logger.info("Starting Groq Script Engine v3.2 HUMAN MODE...")

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
    # System Prompt - FIXED FOR HUMAN TONE + VIRAL
    # ---------------------------
    system_instruction = (
        "You are a viral YouTube Shorts script writer for USA audience. "
        "Write like a real friend talking to you, not like AI or news anchor.\n\n"
        "Niche: Dark Psychology & Mind Tricks.\n\n"
        "CRITICAL RULES:\n"
        "1. 65-85 words script. Max 85 words for 40-55 sec video.\n"
        "2. First 3 words MUST be: You / Your brain / Stop scrolling / 90% people / Never do this\n"
        "3. Add NATURAL pauses with... every 6-8 words. Not robotic.\n"
        "4. Add 2-3 FILLER WORDS naturally: umm, like, you know, right, actually, look\n"
        "5. Include EXACTLY ONE: 'Wait for it...' or 'But here's the twist...'\n"
        "6. Use 'you' at least 5 times. Talk DIRECT to viewer.\n"
        "7. End with casual CTA: Follow for part 2 / Save this / Comment which one shocked you\n"
        "8. Banned words: kill, suicide, murder, blood, death. Use 'dark trick', 'mind hack', 'psychology trap' instead\n"
        "9. Title must be 4-5 words max + 1 emoji. Ex: Your Brain Lies 🧠\n"
        "10. Tone: Casual, dark, like a smart friend warning you in a bar. Use contractions: you're, it's, don't\n"
        "EXAMPLE STYLE: 'Your brain... umm... it lies to you... right? Every single day... but here's the twist... you never notice it... Save this.'\n\n"
        "Return ONLY JSON:\n"
        '{"hook":"",'
        '"script":"",'
        '"seo":{"title":"","description":""},'
        '"broll_keywords":[]'
        "}"
    )

    user_prompt = f"Topic: {topic}. Write for USA audience aged 18-35. Make it sound human, not AI generated."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.85, # FIXED: 0.95 se 0.85 kiya. Human but consistent
            top_p=0.9,
            response_format={"type": "json_object"}
        )

        script_data = json.loads(completion.choices[0].message.content)

        # ---------------------------
        # Validation Safety Layer + Human Post-Processing
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

        # Human tone post-processing
        script_data["script"] = _add_human_tone(script_data["script"])

        if "seo" not in script_data:
            script_data["seo"] = {
                "title": "Brain Secret 🧠",
                "description": "#darkpsychology #mindhacks #psychologyfacts"
            }

        # Word count check for 40-55 sec
        word_count = len(script_data["script"].split())
        if word_count > 85:
            logger.warning(f"Script too long: {word_count} words. Truncating...")
            words = script_data
