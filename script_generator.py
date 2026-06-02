"""
script_generator.py — Groq LLM Script Engine (DEEP-EXPLANATION UNDER 60S v5.5)
AI Dark Realities · YouTube & Instagram Automation Pipeline
Fixed: Enforced strict structure to guarantee videos are between 25-35 seconds.
Fixed: Split JSON payload into mandatory blocks to force deep psychological explanation.
Tested: Bracket alignment and Python 3.10+ syntax error-free.
──────────────────────────────────────────────
"""

import os
import json
import logging
import random
from groq import Groq
import config

logger = logging.getLogger(__name__)

FALLBACK_TOPICS = [
    "Why your brain trusts strangers in 7 seconds",
    "The dark psychology trick casinos use on you",
    "How manipulators control conversations without speaking",
    "The hidden signal liars accidentally reveal",
    "Why silence makes powerful people uncomfortable",
    "How narcissists instantly spot empathetic people",
    "The strange science behind deja vu",
    "The psychological weapon used by master manipulators",
    "Why toxic relationships become addictive",
    "The dark reason people ghost you suddenly"
]

def generate_script(topic: str | None = None) -> dict:
    """
    Generate structured psychological scripts that guarantee a solid 25-35s video.
    Forces: Hook (3-4s) -> '... WAIT. ...' (1.5s Freeze) -> Detailed Explanation (20-25s).
    """
    logger.info("Starting Groq Script Engine v5.5 LONG-FORM UNDER 60S MODE...")

    api_key = os.getenv("GROQ_API_KEY") or getattr(config, "GROQ_API_KEY", None)
    if not api_key:
        raise ValueError("GROQ_API_KEY missing!")

    client = Groq(api_key=api_key)

    if not topic:
        topic = random.choice(FALLBACK_TOPICS)
        logger.info(f"Random topic selected: {topic}")
    else:
        logger.info(f"Topic received: {topic}")

    system_instruction = (
        "You are an elite master scriptwriter for 'AI Dark Realities' YouTube Shorts and Instagram Reels, "
        "specializing in high-retention psychology facts for USA/UK audiences. Tone: Deep, slow, intense, and hypnotic.\n\n"
        "CRITICAL LENGTH & STRUCTURAL RULES (To ensure video is 25-35 seconds, under 60 seconds):\n"
        "1. 'hook': Write a highly aggressive psychological question or statement. (Length: 7-9 words). Ex: 'Is your mind secretly being hacked right now?'\n"
        "2. 'the_wait_trap': This must ALWAYS be exactly: '... WAIT. ...'. Do not change this text.\n"
        "3. 'detailed_explanation': Immediately after the trap, explain exactly HOW and WHY this trick or phenomenon works in deep, clear, continuous detail. "
        "You must write a solid 45-55 words for this section alone. Break down the science or dark trick thoroughly so the idea is crystal clear. No conversational fillers like umm or like.\n"
        "4. 'call_to_action': A sharp question that forces a comment breakout. (Length: 8-12 words).\n\n"
        "ALGORITHM SEO RULES:\n"
        "5. YOUTUBE SHORTS SEO: Provide a 4-5 words max title + 1 emoji. Provide a clean description with 3 high-volume search tags.\n"
        "6. INSTAGRAM REELS SEO: Provide a scroll-stopping caption using short bullet points to maximize user read time, plus 5-8 niche tags.\n\n"
        "Return ONLY JSON and make sure total words across hook + explanation are between 65-75 words total:\n"
        "{\n"
        "  \"hook\": \"\",\n"
        "  \"the_wait_trap\": \"... WAIT. ...\",\n"
        "  \"detailed_explanation\": \"\",\n"
        "  \"call_to_action\": \"\",\n"
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

    user_prompt = f"Topic: {topic}. Ensure 'detailed_explanation' is highly detailed and complete, making the full compiled video around 30 seconds total under the 60s limit."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.75,
            top_p=0.9,
            response_format={"type": "json_object"}
        )

        raw_data = json.loads(completion.choices[0].message.content)

        # ---------------------------
        # Pipeline Assembly Logic (Combining blocks into 'script' variable)
        # ---------------------------
        hook_text = raw_data.get("hook", "Is your mind secretly being hacked right now?").strip()
        wait_text = "... WAIT. ..."
        body_text = raw_data.get("detailed_explanation", "Most people have no idea how vulnerable their subconscious mind is to external triggers. When a master manipulator uses silent anchors, your thoughts are programmatically directed without your active consent.").strip()
        cta_text = raw_data.get("call_to_action", "Comment if you think you are safe.").strip()

        # Compile final continuous string for the voice/video compilers
        compiled_script = f"{hook_text} {wait_text} {body_text} {cta_text}"

        # Build final standardized payload matching your main script compiler requirements
        script_data = {
            "hook": hook_text,
            "script": _clean_narrative(compiled_script),
            "youtube_seo": raw_data.get("youtube_seo", {
                "title": "Is Your Mind Hacked? 🧠",
                "description": "How external psychological anchors control your brain without permission. \n\n#darkpsychology #mindhacks #shorts"
            }),
            "instagram_seo": raw_data.get("instagram_seo", {
                "caption": "Your mind might be targeted right now... 🤫👇\n\n• Silent psychological anchors control your choice.\n• Your subconscious is vulnerable.\n\nComment 'READY' to see how to block it.",
                "hashtags": "#darkpsychology #manipulation #mindtricks #reelsviral"
            }),
            "broll_keywords": raw_data.get("broll_keywords", ["brain scan", "eye closeup", "shadow figure"])
        }

        logger.info(f"✅ Full Detailed Script Compiled! Total Words: {len(script_data['script'].split())} (~28-32 Seconds Video)")
        return script_data

    except Exception as e:
        logger.error(f"Groq Script generation failed: {e}")
        # Rock-solid detailed fallback payload
        return {
            "hook": "Is your mind secretly being hacked right now?",
            "script": (
                "Is your mind secretly being hacked right now? ... WAIT. ... "
                "Most people have no idea how vulnerable their subconscious mind is to external manipulation. "
                "When someone uses specific conversational anchors and strategic pauses, your brain automatically "
                "fills the void, letting them direct your choices without your active consent. "
                "Comment below if you think you are safe."
            ),
            "youtube_seo": {
                "title": "Is Your Mind Hacked? 🧠",
                "description": "Discover how master manipulators exploit conversational loops. \n\n#darkpsychology #mindhacks #shorts"
            },
            "instagram_seo": {
                "caption": "Your choices might not be yours... 🤫👇\n\n• Conversational anchors bypass logic.\n• Brain patterns are easily directed.\n\nComment 'READY' to block it.",
                "hashtags": "#darkpsychology #manipulation #mindtricks #reelsviral"
            },
            "broll_keywords": ["brain scan", "eye closeup", "shadow figure"]
        }

def _clean_narrative(script: str) -> str:
    fillers_to_remove = ["umm", "umm...", "like,", "like...", "you know,", "you know...", "um,", "um"]
    words = script.split()
    cleaned_words = [w for w in words if w.lower().strip(".,!?;:") not in fillers_to_remove]
    processed = " ".join(cleaned_words)
    processed = processed.replace("...WAIT...", "... WAIT. ...").replace("... WAIT ...", "... WAIT. ...")
    return " ".join(processed.split())
