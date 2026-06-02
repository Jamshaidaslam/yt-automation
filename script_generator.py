"""
script_generator.py — Groq LLM Script Engine (ULTRA-SHORT HIGH RETENTION v5.0)
AI Dark Realities · YouTube & Instagram Automation Pipeline
Fixed: Tightened script word limits (50-55 words max) for perfect 22-24s duration.
Fixed: Implemented split-platform SEO architectures (YT Search vs Insta Loop-Count).
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
    Generate tight, high-speed viral scripts. 
    Flow: Immediate Hook -> Programmatic WAIT -> Crystal Clear Explanation.
    """
    logger.info("Starting Groq Script Engine v5.0 SHORT-FORM SPEED MODE...")

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
        "You are an elite multi-platform content strategist for 'AI Dark Realities', "
        "writing high-retention short-form videos for USA/UK audiences. Tone: Deep, casual, intense, and hypnotic.\n\n"
        "Niche: Dark Psychology & Mind Tricks.\n\n"
        "CRITICAL SHORT-FORM STRUCTURAL RULES:\n"
        "1. THE HOOK (0-4s): Start directly with a brutal, aggressive psychological fact. "
        "First 3 words MUST catch instant attention (e.g., 'Your brain is...', 'Stop doing this...'). Length: 8-10 words max.\n"
        "2. THE TRAP (4-5.5s): Immediately after the hook sentence, you MUST write the exact string: '... WAIT. ...'. This is a mandatory code marker.\n"
        "3. THE CRYSTAL CLEAR BODY (5.5-20s): Explain the complete psychological idea in a continuous, fast-paced fluid flow. "
        "DO NOT use conversational fillers like 'umm', 'like', 'you know', or 'um'. Deliver pure value cleanly so the idea is crystal clear.\n"
        "4. THE CALL TO ACTION (20-23s): End with a sharp, high-conversion question or open-loop that forces comments (e.g., 'Drop your thoughts below').\n"
        "5. STRICT CEILING LIMIT: Total script text must be 50-55 words maximum. Do not exceed this to protect video duration.\n"
        "6. BANNED WORDS: kill, suicide, murder, blood, death. Use 'dark trick', 'mind hack', 'psychology trap'.\n\n"
        "ALGORITHM SEO RULES:\n"
        "7. YOUTUBE SHORTS SEO:\n"
        "   - 'title': 4-5 words max + 1 high-retention emoji. Optimized for CTR on the Shorts Shelf. Ex: Your Brain Lies 🧠\n"
        "   - 'description': Packed with search keywords and exactly 3-4 clean tags. No emojis in tags.\n"
        "8. INSTAGRAM REELS SEO:\n"
        "   - 'caption': An aggressive psychological hook text using short bullet points to force the user to click the 'More' button (boosting background loops), ending with a clear CTA (e.g., 'Comment READY').\n"
        "   - 'hashtags': 5-8 hyper-targeted reels tags separated by spaces.\n\n"
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

    user_prompt = f"Topic: {topic}. Write for USA audience. Strictly enforce: Hook -> '... WAIT. ...' -> Crystal Clear, filler-free fluid explanation. Max 55 words total."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            top_p=0.9,
            response_format={"type": "json_object"}
        )

        script_data = json.loads(completion.choices[0].message.content)

        if not isinstance(script_data.get("broll_keywords"), list) or len(script_data["broll_keywords"]) < 3:
            script_data["broll_keywords"] = ["brain scan", "eye closeup", "shadow figure"]

        if "hook" not in script_data or not script_data["hook"]:
            script_data["hook"] = "Your brain is hiding this from you."

        if "script" not in script_data:
            script_data["script"] = (
                f"{script_data['hook']} ... WAIT. ... "
                "Most people never realize how easily their subconscious is manipulated. "
                "When someone stays perfectly silent, your mind panic starts. "
                "Save this video to remember."
            )
        else:
            if "... WAIT. ..." not in script_data["script"] and "WAIT." not in script_data["script"]:
                hook_text = script_data["hook"]
                body_text = script_data["script"].replace(hook_text, "").strip()
                script_data["script"] = f"{hook_text} ... WAIT. ... {body_text}"

        script_data["script"] = _clean_narrative(script_data["script"])

        # Strict Word count ceiling clip for Shorts pacing
        words = script_data["script"].split()
        if len(words) > 58:
            logger.warning("Script exceeded maximum short-form length. Clipping programmatically...")
            script_data["script"] = " ".join(words[:54]) + "."

        if "youtube_seo" not in script_data or not script_data["youtube_seo"].get("title"):
            script_data["youtube_seo"] = {
                "title": "The Silent Power 🧠",
                "description": "Why silence makes powerful people uncomfortable. Master this dark psychology trick today. \n\n#darkpsychology #mindhacks #psychologyfacts #shorts"
            }
            
        if "instagram_seo" not in script_data or not script_data["instagram_seo"].get("caption"):
            script_data["instagram_seo"] = {
                "caption": "Your silence is actually terrifying to them... Here is why. 🤫👇\n\n• It breaks their control loop.\n• It forces deep overthinking.\n\nDrop a 'READY' in the comments if you want the next part.",
                "hashtags": "#darkpsychology #manipulation #mindtricks #reelsviral #psychologyfacts"
            }

        logger.info(f"✅ Fast-Paced Script Locked! Final Word Count: {len(script_data['script'].split())}")
        return script_data

    except Exception as e:
        logger.error(f"Groq Script generation failed: {e}")
        return {
            "hook": "Your silence scares them because they cannot control you.",
            "script": (
                "Your silence scares them because they cannot control you. ... WAIT. ... "
                "When you speak, you reveal your boundaries. But when you remain perfectly silent, "
                "it creates an information vacuum. This psychological pressure forces them to panic. "
                "Save this video to remember this hack."
            ),
            "youtube_seo": {
                "title": "The Silent Power 🧠",
                "description": "Why silence makes powerful people uncomfortable. Discover the dark psychology of mind hacks. \n\n#darkpsychology #mindhacks #psychologyfacts #shorts"
            },
            "instagram_seo": {
                "caption": "Your silence is making them uncomfortable... Here is the dark psychology reason why. 🤫👇\n\n• It breaks their control loop.\n• It turns you into an absolute mystery.\n\nComment 'READY' if you want the next breakdown.",
                "hashtags": "#darkpsychology #manipulation #mindtricks #reelsviral #psychologyfacts"
            },
            "broll_keywords": ["brain scan", "eye closeup", "shadow figure"]
        }

def _clean_narrative(script: str) -> str:
    fillers_to_remove = ["umm", "umm...", "like,", "like...", "you know,", "you know...", "actually,", "right,", "um,", "um", "furthermore", "additionally"]
    words = script.split()
    cleaned_words = [w for w in words if w.lower().strip(".,!?;:") not in fillers_to_remove]
    processed = " ".join(cleaned_words)
    processed = processed.replace("...WAIT...", "... WAIT. ...").replace("... WAIT ...", "... WAIT. ...")
    return " ".join(processed.split())
