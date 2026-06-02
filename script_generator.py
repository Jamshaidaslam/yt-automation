"""
script_generator.py — Groq LLM Script Engine (SUSPENSE TRAP + AUTOMATED HOOK v3.5)
AI Dark Realities · YouTube Automation Pipeline
Optimized for USA audience + Dynamic Hook & Silent Trap + Human Tone
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
    Forces a high-retention 3-4s killer hook followed by a dramatic freeze trap.
    """

    logger.info("Starting Groq Script Engine v3.5 CRITICAL HOOK MODE...")

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
    # System Prompt - SUSPENSE TRAP & PATTERN INTERRUPT
    # ---------------------------
    system_instruction = (
        "You are an elite scriptwriter for 'AI Dark Realities', specializing in high-retention short-form videos for USA/UK audiences. "
        "Write like a real friend talking to you—casual, dark, like a smart friend warning you in a bar. Use contractions (you're, it's, don't).\n\n"
        "Niche: Dark Psychology & Mind Tricks.\n\n"
        "CRITICAL STRUCTURAL RULES FOR EVERY SCRIPT:\n"
        "1. THE KILLER HOOK (0-4s): Start directly with a shocking, brutal truth, fear-trigger, or dark psychology paradox. "
        "First 3 words MUST be highly aggressive: You / Your brain / Stop scrolling / 90% people / Never do this. (Length: 8-12 words max).\n"
        "2. THE DRAMATIC TRAP (4-6s): Immediately after the hook sentence, you MUST inject the exact freeze phrase: '... WAIT. ...'. "
        "This is a non-negotiable rule to trigger a physical silence in the audio engine.\n"
        "3. THE HYPNOTIC BODY (6-25s): Deliver deep, slow, analytical value about the topic. Add natural pauses with '...' every 6-8 words. "
        "Blend 2-3 filler words naturally: umm, like, you know, right, actually.\n"
        "4. THE OPEN LOOP OUTRO (25-32s): End with a high-conversion call to action that forces comments: Follow for part 2 / Save this / Comment if you are ready.\n"
        "5. MAX WORDS: Total script must be between 65-80 words max to allow room for the dramatic silence trap.\n"
        "6. BANNED WORDS: kill, suicide, murder, blood, death. Use 'dark trick', 'mind hack', 'psychology trap' instead.\n"
        "7. TITLE: Must be 4-5 words max + 1 emoji. Ex: Your Brain Lies 🧠\n\n"
        "EXAMPLE STUCTURE OUTPUT:\n"
        "\"hook\": \"Your silence scares them... because they can't control you.\",\n"
        "\"script\": \"Your silence scares them... because they can't control you. ... WAIT. ... When you talk, you reveal your limits... right? But when you stay quiet... umm... you become a complete mystery. It forces them to overthink every move... Save this.\"\n\n"
        "Return ONLY JSON:\n"
        '{"hook":"",'
        '"script":"",'
        '"seo":{"title":"","description":""},'
        '"broll_keywords":[]'
        "}"
    )

    user_prompt = f"Topic: {topic}. Write for USA audience aged 18-35. Make the hook punchy and ensure the '... WAIT. ...' string is placed exactly after the hook sentence."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.82,
            top_p=0.9,
            response_format={"type": "json_object"}
        )

        script_data = json.loads(completion.choices[0].message.content)

        # ---------------------------
        # Validation Safety Layer + Automated Fallbacks
        # ---------------------------
        if not isinstance(script_data.get("broll_keywords"), list) or len(script_data["broll_keywords"]) < 3:
            script_data["broll_keywords"] = ["brain scan", "eye closeup", "shadow figure", "neon brain"]

        if "hook" not in script_data or len(script_data["hook"].split()) < 3:
            script_data["hook"] = "Your brain is hiding this from you."

        # Ensure the dramatic "... WAIT. ..." trap always exists in the script text
        if "script" not in script_data:
            script_data["script"] = (
                f"{script_data['hook']} ... WAIT. ... "
                "Most people... never realize this hidden pattern... "
                "Your subconscious... reacts first, your mind follows later... "
                "Comment if you are ready..."
            )
        else:
            # Force post-processing to inject the trap if LLM forgot it
            if "... WAIT. ..." not in script_data["script"] and "WAIT." not in script_data["script"]:
                logger.warning("LLM omitted the trap. Injecting freeze string programmatically.")
                hook_text = script_data["hook"]
                body_text = script_data["script"].replace(hook_text, "").strip()
                script_data["script"] = f"{hook_text} ... WAIT. ... {body_text}"

        # Clean double spaces and standardize tone
        script_data["script"] = _add_human_tone(script_data["script"])

        if "seo" not in script_data:
            script_data["seo"] = {
                "title": "The Silent Power 🧠",
                "description": "#darkpsychology #mindhacks #psychologyfacts"
            }

        # Strict Word count ceiling for safety
        words = script_data["script"].split()
        if len(words) > 85:
            logger.warning(f"Script too long. Truncating to preserve retention pace...")
            script_data["script"] = " ".join(words[:82]) + "..."

        logger.info(f"✅ Suspense Script generated successfully! Total Words: {len(script_data['script'].split())}")
        return script_data

    except Exception as e:
        logger.error(f"Groq Script generation failed: {e}")
        # Rock-solid fallback loop maintaining the suspense structure
        return {
            "hook": "Your silence scares them... because they can't control you.",
            "script": (
                "Your silence scares them... because they can't control you. ... WAIT. ... "
                "When you talk... you reveal your limits... right? But when you stay quiet... "
                "umm... you become a complete mystery. It forces them to overthink every single move... "
                "Save this video for later."
            ),
            "seo": {
                "title": "The Silent Power 🧠",
                "description": "#darkpsychology #mindhacks #psychologyfacts"
            },
            "broll_keywords": ["brain scan", "eye closeup", "shadow figure", "neon brain"]
        }

def _add_human_tone(script: str) -> str:
    """
    Post-processing: Normalizes AI transitions into casual bar-talk patterns.
    """
    replacements = {
        "Additionally": "Also",
        "Furthermore": "Plus",
        "However": "But",
        "Therefore": "So",
        "Consequently": "That's why",
        "In conclusion": "Look",
        "Moreover": "And"
    }

    for ai_word, human_word in replacements.items():
        script = script.replace(ai_word, human_word)

    # Standardize spaces around the trap
    script = script.replace("...WAIT...", "... WAIT. ...").replace("... WAIT ...", "... WAIT. ...")
    return " ".join(script.split())
