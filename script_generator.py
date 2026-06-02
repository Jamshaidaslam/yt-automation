"""
script_generator.py — Groq LLM Script Engine (DUAL-ALGORITHM SEO v4.0)
AI Dark Realities · YouTube Automation Pipeline
Optimized for USA audience + Dynamic Hook & Silent Trap + YT & Insta Split SEO
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
    Generate viral YouTube Shorts & Instagram Reels script using Groq API.
    Splits SEO architectures based on distinct platform algorithms.
    """

    logger.info("Starting Groq Script Engine v4.0 DUAL-ALGORITHM SEO MODE...")

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
    # System Prompt - WITH DUAL SEO ARCHITECTURES
    # ---------------------------
    system_instruction = (
        "You are an elite multi-platform content strategist and scriptwriter for 'AI Dark Realities', "
        "specializing in short-form videos for USA/UK audiences. Write like a real friend talking—casual, dark, and intense.\n\n"
        "Niche: Dark Psychology & Mind Tricks.\n\n"
        "CRITICAL STRUCTURAL RULES:\n"
        "1. THE KILLER HOOK (0-4s): Start directly with a shocking, brutal truth, fear-trigger, or dark psychology paradox. "
        "First 3 words MUST be highly aggressive: You / Your brain / Stop scrolling / 90% people / Never do this. (Length: 8-12 words max).\n"
        "2. THE DRAMATIC TRAP (4-6s): Immediately after the hook sentence, you MUST inject the exact freeze phrase: '... WAIT. ...'.\n"
        "3. THE HYPNOTIC BODY (6-25s): Deliver deep, slow, analytical value about the topic. Add natural pauses with '...' every 6-8 words. "
        "Blend 2-3 filler words naturally: umm, like, you know, right.\n"
        "4. THE OPEN LOOP OUTRO (25-32s): End with a high-conversion call to action that forces comments: Follow for part 2 / Save this / Comment if you are ready.\n"
        "5. MAX WORDS: Total script must be between 65-80 words max.\n"
        "6. BANNED WORDS: kill, suicide, murder, blood, death. Use 'dark trick', 'mind hack', 'psychology trap' instead.\n\n"
        "ALGORITHM SEO RULES:\n"
        "7. YOUTUBE SHORTS SEO (Search & Discovery Algorithm Optimized):\n"
        "   - 'title': Must be 4-5 words max + 1 high-retention emoji. Designed for high CTR on the Shorts Shelf. Ex: Your Brain Lies 🧠\n"
        "   - 'description': Packed with high-volume search intent keywords, clean semantic explanation, and exactly 3-4 highly relevant search hashtags. No emojis in tags.\n"
        "8. INSTAGRAM REELS SEO (Engagement & Watch-Time Loop Algorithm Optimized):\n"
        "   - 'caption': An aggressive psychological micro-hook that stops the scroll, triggers users to click the 'More' button (boosting watch-time loops), uses bullet points, contains a high-converting comment trigger CTA (e.g., 'Comment READY below'), and speaks to immediate human curiosity.\n"
        "   - 'hashtags': 5-8 hyper-targeted viral reels niche hashtags separated by spaces (e.g., #darkpsychology #manipulation).\n\n"
        "Return ONLY JSON:\n"
        "{\n"
        "  \"hook\": \"\",\n"
        "  \"script\": \"\",\n"
        "  \"youtube_seo\": {\n"
        "    \"title\": \"\",\n"
        "    \"description\": \"\"\n"
        "  },\n"
        "  \"instagram_seo\": {\n"
        "    \"caption\": \"\",\n"
        "    \"hashtags\": \"\"\n"
        "  },\n"
        "  \"broll_keywords\": []\n"
        "}"
    )

    user_prompt = f"Topic: {topic}. Write for USA audience aged 18-35. Ensure youtube_seo satisfies the search algorithm and instagram_seo satisfies the loop/engagement engine."

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

        # Ensure the dramatic freeze trap exists
        if "script" not in script_data:
            script_data["script"] = (
                f"{script_data['hook']} ... WAIT. ... "
                "Most people... never realize this hidden pattern... "
                "Your subconscious... reacts first, your mind follows later... "
                "Comment if you are ready..."
            )
        else:
            if "... WAIT. ..." not in script_data["script"] and "WAIT." not in script_data["script"]:
                logger.warning("LLM omitted the trap. Injecting freeze string programmatically.")
                hook_text = script_data["hook"]
                body_text = script_data["script"].replace(hook_text, "").strip()
                script_data["script"] = f"{hook_text} ... WAIT. ... {body_text}"

        # Apply human tone transformations
        script_data["script"] = _add_human_tone(script_data["script"])

        # --- DUAL-ALGORITHM SEO VALIDATION LOOP ---
        if "youtube_seo" not in script_data or not script_data["youtube_seo"].get("title"):
            script_data["youtube_seo"] = {
                "title": "The Silent Power 🧠",
                "description": f"Why silence makes powerful people uncomfortable. Master this dark psychology mind hack today. \n\n#darkpsychology #mindhacks #psychologyfacts #shorts"
            }
            
        if "instagram_seo" not in script_data or not script_data["instagram_seo"].get("caption"):
            script_data["instagram_seo"] = {
                "caption": "Your silence is actually terrifying to them... Here is the hidden mind trap why. 🤫👇\n\n• It disrupts their ego.\n• It forces them to overthink.\n• It shields your next move.\n\nDrop a 'READY' in the comments if you want to unlock the full breakdown.",
                "hashtags": "#darkpsychology #manipulation #mindtricks #reelsviral #sigmamale #psychologyfacts"
            }

        # Strict Word count ceiling for safety
        words = script_data["script"].split()
        if len(words) > 85:
            logger.warning(f"Script too long. Truncating to preserve retention pace...")
            script_data["script"] = " ".join(words[:82]) + "..."

        logger.info(f"✅ Dual-SEO Strategy Generated Successfully! Total Words: {len(script_data['script'].split())}")
        return script_data

    except Exception as e:
        logger.error(f"Groq Script generation failed: {e}")
        # Rock-solid fallback loop maintaining dual data
        return {
            "hook": "Your silence scares them... because they can't control you.",
            "script": (
                "Your silence scares them... because they can't control you. ... WAIT. ... "
                "When you talk... you reveal your limits... right? But when you stay quiet... "
                "umm... you become a complete mystery. It forces them to overthink every single move... "
                "Save this video for later."
            ),
            "youtube_seo": {
                "title": "The Silent Power 🧠",
                "description": "Why silence makes powerful people uncomfortable. Discover the dark psychology of mind hacks. \n\n#darkpsychology #mindhacks #psychologyfacts #shorts"
            },
            "instagram_seo": {
                "caption": "Your silence is making them uncomfortable... Here is the dark psychology reason why. 🤫👇\n\n• It breaks their control loop.\n• It turns you into an absolute mystery.\n\nComment 'READY' if you are ready for part 2.",
                "hashtags": "#darkpsychology #manipulation #mindtricks #reelsviral #psychologyfacts"
            },
            "broll_keywords": ["brain scan", "eye closeup", "shadow figure", "neon brain"]
        }

def _add_human_tone(script: str) -> str:
    """Post-processing: Normalizes AI transitions into casual bar-talk patterns."""
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

    script = script.replace("...WAIT...", "... WAIT. ...").replace("... WAIT ...", "... WAIT. ...")
    return " ".join(script.split())
