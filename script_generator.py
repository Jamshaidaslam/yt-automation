"""
script_generator.py — Ultimate Viral Dark Psychology Engine (v2.0 - TOPIC ROTATION FIXED)
AI Dark Realities · USA/UK Viral Shorts Generator
───────────────────────────────────────────────────────────────────────────────────

FIXES v2.0:
  - Added TOPIC_POOL: 40 unique dark psychology topics
  - Topic rotation using date-based seeding — each day gets a different topic
    automatically, so no two consecutive runs produce the same video
  - GitHub Actions runs 3x/day — each run picks a different slot topic
  - Manual --topic override still works as before
"""

import json
import os
import re
import logging
import hashlib
import random
from datetime import datetime
from groq import Groq

logger = logging.getLogger(__name__)

# ─── 40 Unique Dark Psychology Topics for Auto-Rotation ───────────────────────
TOPIC_POOL = [
    "How your phone uses dark psychology as a dopamine trap",
    "The manipulation tactic every narcissist uses on you",
    "Why you can't stop scrolling — the dark truth",
    "How big tech hijacks your brain's reward system",
    "The silent psychological trick used in every ad you see",
    "Why toxic relationships feel impossible to leave",
    "How social media makes you feel inferior on purpose",
    "The fear loop your brain is stuck in right now",
    "How your insecurities are being sold back to you",
    "The dark reason you seek validation from strangers online",
    "Why your attention is the most valuable thing you own",
    "How algorithms decide what emotions you feel today",
    "The psychological trick behind every like and notification",
    "Why you compare yourself to others and can't stop",
    "How streaming services are designed to steal your sleep",
    "The dark truth about why you procrastinate",
    "How cults use the same tricks as social media",
    "Why your phone makes you feel lonely on purpose",
    "The manipulation behind every 'limited time offer' you see",
    "How your childhood trauma is being exploited by marketers",
    "The dark psychology behind why gossip feels good",
    "Why you trust strangers on the internet more than real people",
    "How your phone tracks your emotional state without asking",
    "The psychological reason you can't say no to people",
    "Why binge watching is designed to break your willpower",
    "How dark patterns in apps trick you into spending money",
    "The real reason news channels want you angry",
    "Why your brain is addicted to bad news",
    "How fake urgency controls every decision you make",
    "The identity trap social media sets for you",
    "Why the people who love you most trigger you the most",
    "How your phone is more addictive than cocaine",
    "The dark truth about why you overshare online",
    "How parasocial relationships hijack your emotional brain",
    "Why you feel empty after hours of scrolling",
    "The psychological reason you can't delete social media",
    "How dark UX design steals hours from your life daily",
    "Why your brain can't tell the difference between real and fake threats",
    "The manipulation tactic behind every viral outrage post",
    "How your deepest fears are used to control your behavior",
]


def pick_topic_for_run() -> str:
    """
    Picks a unique topic based on current date + hour slot.
    - 3 runs per day (morning / afternoon / primetime) each get different topic
    - Cycles through all 40 topics before repeating
    - Fully deterministic — same run time always picks same topic (safe for retries)
    """
    now = datetime.utcnow()
    
    # Map hour to slot: 0-11 = slot 0, 12-17 = slot 1, 18-23 = slot 2
    if now.hour < 12:
        slot = 0
    elif now.hour < 18:
        slot = 1
    else:
        slot = 2

    # day_index cycles 0..N — ensures different topic each day
    day_of_year = now.timetuple().tm_yday
    year = now.year

    # Unique index = (days since epoch * 3 slots) + current slot
    days_since_epoch = (year - 2024) * 365 + day_of_year
    topic_index = (days_since_epoch * 3 + slot) % len(TOPIC_POOL)

    chosen = TOPIC_POOL[topic_index]
    logger.info(f"📋 Auto-selected topic #{topic_index}: {chosen}")
    return chosen


def generate_script(topic: str = "") -> dict:
    # If no topic provided, auto-pick from rotation pool
    if not topic or not topic.strip():
        topic = pick_topic_for_run()

    logger.info(f"🧠 Generating script for: [{topic}]")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable.")

    client = Groq(api_key=api_key)

    system_prompt = """You are a world-class viral content architect specializing in Dark Psychology and high-retention short-form videos.
Your mission is to engineer a highly addictive script with dramatic pacing.

VOICEOVER REQUIREMENTS:
- MUST contain between 90 and 120 words total.
- Use commas and punctuation for natural breathing pauses.
- End with a sentence that loops back into the opening hook.
- Write as if speaking directly to the viewer — use "you" and "your".

SCENE REQUIREMENTS:
- Generate EXACTLY 12 scenes with short portrait-oriented Pexels visual queries.

STRICT OUTPUT FORMAT:
- Return ONLY valid JSON. No markdown, no explanation.

JSON STRUCTURE:
{
  "title": "High CTR viral title under 60 characters",
  "voiceover": "The full 90-120 word continuous narrative.",
  "scenes": [
    {"scene_number": 1, "visual_query": "dark silhouette face shadow"},
    {"scene_number": 2, "visual_query": "smartphone screen glow dark room"},
    {"scene_number": 3, "visual_query": "anxious person hands typing"},
    {"scene_number": 4, "visual_query": "macro human eye dilating"},
    {"scene_number": 5, "visual_query": "mysterious concrete alleyway dark"},
    {"scene_number": 6, "visual_query": "abstract digital matrix code"},
    {"scene_number": 7, "visual_query": "person head in hands stressed"},
    {"scene_number": 8, "visual_query": "security camera red blinking light"},
    {"scene_number": 9, "visual_query": "silhouette walking away fog"},
    {"scene_number": 10, "visual_query": "close up phone screen scrolling"},
    {"scene_number": 11, "visual_query": "moody neon rain reflection"},
    {"scene_number": 12, "visual_query": "dark psychological realization portrait"}
  ]
}"""

    user_prompt = (
        f"Create a high-retention 12-scene dark psychology loop script about: {topic}. "
        f"Voiceover must be 90-120 words with natural punctuation pauses."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.82,       # Slightly higher = more variety between runs
        max_tokens=1500,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if not match:
            raise RuntimeError(f"Could not parse JSON from Groq: {raw_output}")
        data = json.loads(match.group(0))

    logger.info(f"✅ Script generated | Title: {data.get('title', 'N/A')}")
    return data
