"""
script_generator.py — Groq LLM Script Engineering Engine (VIRAL SHORT-FORM RULES v3.0)
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

# Advanced fallback topics

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

def generate_script(topic: str | None = None) -> dict:
"""
Generate high-retention mystery style YouTube Shorts scripts.
Returns structured JSON.
"""

```
logger.info("Initializing Groq Viral Script Engine v3.0")

api_key = os.getenv("GROQ_API_KEY") or getattr(config, "GROQ_API_KEY", None)

if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is missing!")

client = Groq(api_key=api_key)

if not topic:
    topic = random.choice(FALLBACK_TOPICS)
    logger.info(f"Selected random viral topic: {topic}")
else:
    logger.info(f"Generating script for topic: {topic}")

system_instruction = (
    "You are an elite viral YouTube Shorts script writer.\n"
    "Target Audience: USA\n"
    "Niche: Psychology, Human Behavior, Mystery, Brain Facts.\n\n"

    "PRIMARY GOAL:\n"
    "Maximize retention, rewatches, comments, curiosity and watch time.\n\n"

    "STRICT RULES:\n"
    "1. Script length: 90-130 words.\n"
    "2. First sentence MUST create an unanswered mystery.\n"
    "3. Create suspense and curiosity immediately.\n"
    "4. Include at least 3 curiosity gaps.\n"
    "5. Never reveal everything at once.\n"
    "6. Use short punchy sentences.\n"
    "7. Make viewers feel they discovered a hidden secret.\n"
    "8. Use emotional triggers: fear, surprise, curiosity, power.\n"
    "9. Use the word 'you' frequently.\n"
    "10. Sound cinematic and mysterious.\n"
    "11. Include EXACTLY ONE pattern interrupt:\n"
    "   'Wait for it...' OR 'But here's the twist...'\n"
    "12. End with a strong CTA.\n\n"

    "STRUCTURE:\n"
    "Hook\n"
    "Hidden Fact\n"
    "Suspense Build-Up\n"
    "Pattern Interrupt\n"
    "Twist Reveal\n"
    "CTA\n\n"

    "CTA MUST BE ONE OF:\n"
    "- Follow for part 2\n"
    "- Save this before you forget\n"
    "- Comment if you noticed this too\n\n"

    "BANNED WORDS:\n"
    "kill, murder, suicide, blood, weapon\n\n"

    "Generate realistic psychology-based content.\n"
    "Avoid impossible supernatural claims.\n\n"

    "Return ONLY valid JSON.\n"
    "{\n"
    '  "hook":"",\n'
    '  "script":"",\n'
    '  "seo":{\n'
    '      "title":"",\n'
    '      "description":""\n'
    "  },\n"
    '  "broll_keywords":["","","","",""]\n'
    "}"
)

user_prompt = (
    f"Topic: {topic}\n\n"
    "Generate the complete JSON script now."
)

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

    raw_response = completion.choices[0].message.content

    script_data = json.loads(raw_response)

    logger.info("Script generated successfully.")

    # Validation
    if (
        "broll_keywords" not in script_data
        or not isinstance(script_data["broll_keywords"], list)
        or len(script_data["broll_keywords"]) < 3
    ):
        script_data["broll_keywords"] = [
            "dark psychology",
            "mystery silhouette",
            "human behavior",
            "brain secrets",
            "cinematic shadow"
        ]

    if "hook" not in script_data:
        script_data["hook"] = "Your brain is hiding something from you."

    if "script" not in script_data:
        script_data["script"] = (
            "Your brain notices things before you do. "
            "Most people never realize this hidden pattern. "
            "Wait for it... "
            "The strange part is that your subconscious already reacted. "
            "Comment if you noticed this too."
        )

    if "seo" not in script_data:
        script_data["seo"] = {
            "title": "Brain Secret 🧠",
            "description": "#darkpsychology #mindhacks #psychologyfacts"
        }

    return script_data

except Exception as e:

    logger.error(f"Groq generation failed: {e}")

    return {
        "hook": "Your brain already knows this secret.",
        "script": (
            "Your brain notices patterns before you consciously see them. "
            "Most people completely miss this hidden signal. "
            "Wait for it... "
            "Researchers discovered your subconscious reacts first and your conscious mind follows later. "
            "That's why some people instantly feel trustworthy or suspicious. "
            "Comment if you noticed this too."
        ),
        "seo": {
            "title": "Brain Secret 🧠",
            "description": (
                "The hidden psychology your brain uses every day. "
                "#darkpsychology #mindhacks #psychologyfacts"
            )
        },
        "broll_keywords": [
            "dark psychology",
            "brain mystery",
            "human behavior",
            "cinematic shadow",
            "neural glow"
        ]
    }
```
