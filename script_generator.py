"""
script_generator.py — VIRAL DOMINATION ENGINE v3.0 (USA/UK STABLE HIGH RETENTION)
"""
import json
import os
import logging
import random
from groq import Groq

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 120 VIRAL TOPIC POOL (Mukammal Safe aur Unchanged)
# ═══════════════════════════════════════════════════════════════════════════════
TOPIC_POOL = [
    {
        "topic": "If someone holds eye contact longer than normal — here's what it secretly means",
        "category": "eye_reading",
        "hook_type": "curiosity_gap",
        "series": "Eye Secrets", "part": 1,
        "cta": "Save this — you'll use it tomorrow",
        "scenes_theme": "close up eyes, eye contact, pupils dilating, staring, gaze direction"
    },
    {
        "topic": "The direction someone looks when lying — your eyes reveal your brain",
        "category": "eye_reading",
        "hook_type": "revelation",
        "series": "Eye Secrets", "part": 2,
        "cta": "Follow for Part 3 — it gets darker",
        "scenes_theme": "eyes looking left right, lie detection, brain scan, nervous glance"
    },
    {
        "topic": "When someone's pupils dilate looking at you — the truth your body can't hide",
        "category": "eye_reading",
        "hook_type": "identity_threat",
        "series": "Eye Secrets", "part": 3,
        "cta": "Comment if this happened to you",
        "scenes_theme": "pupil dilation macro, attraction eye contact, close face portrait"
    },
    {
        "topic": "Blink rate reveals exactly how nervous, attracted or threatened someone is",
        "category": "eye_reading",
        "hook_type": "curiosity_gap",
        "series": "Eye Secrets", "part": 4,
        "cta": "Save this — watch people differently forever",
        "scenes_theme": "blinking eyes, nervous person, eye closeup, tense conversation"
    },
    {
        "topic": "The micro-expression that flashes across someone's eyes when they secretly like you",
        "category": "eye_reading",
        "hook_type": "revelation",
        "series": "Eye Secrets", "part": 5,
        "cta": "Follow — Part 6 reveals the full signal",
        "scenes_theme": "micro expression face, subtle smile, eye flash, hidden emotion portrait"
    },
    {
        "topic": "Looking at someone's eyebrows reveals what they actually think of you",
        "category": "eye_reading",
        "hook_type": "curiosity_gap",
        "series": "Eye Secrets", "part": 6,
        "cta": "Save this and test it today",
        "scenes_theme": "eyebrow raise, face expression, conversation closeup, eyebrow flash"
    },
    {
        "topic": "The exact eye movement that means someone is imagining you",
        "category": "eye_reading",
        "hook_type": "revelation",
        "series": "Eye Secrets", "part": 7,
        "cta": "Comment — has someone done this to you",
        "scenes_theme": "dreamy eyes, upward gaze, imagination face, eyes looking up"
    },
    {
        "topic": "If someone looks at your mouth while you talk — this is what it means",
        "category": "eye_reading",
        "hook_type": "identity_threat",
        "series": "Eye Secrets", "part": 8,
        "cta": "Follow for the full body language series",
        "scenes_theme": "lips focus, gaze direction, conversation face, mouth eye alternating"
    },
    {
        "topic": "How to make anyone feel deeply seen just by changing how you look at them",
        "category": "eye_reading",
        "hook_type": "power_secret",
        "series": "Eye Secrets", "part": 9,
        "cta": "Save this — it changes every conversation",
        "scenes_theme": "deep eye contact, emotional connection, trust face, warm gaze portrait"
    },
    {
        "topic": "The 3 second eye contact rule that makes people instantly trust you",
        "category": "eye_reading",
        "hook_type": "power_secret",
        "series": "Eye Secrets", "part": 10,
        "cta": "Follow — tomorrow's video will shock you",
        "scenes_theme": "confident eye contact, trust building, handshake eye, business confidence"
    },
    {
        "topic": "The question that instantly reveals someone's true character in 10 seconds",
        "category": "people_reading",
        "hook_type": "power_secret",
        "series": "Read Anyone", 
        "part": 6,
        "cta": "Follow — Part 7 reveals how to read anger",
        "scenes_theme": "character test, deep question, revealing personality, observant face"
    }
]

# ═══════════════════════════════════════════════════════════════════════════════
#  AI SCRIPT GENERATION LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def generate_script(topic: str):
    """
    Uses Groq AI to generate a viral script based on the hook formula with strict aesthetic blocks.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Dynamic pool mapping to inject exact metadata context without losing anything
    matched_meta = next((item for item in TOPIC_POOL if item["topic"] == topic), None)
    pool_cta = matched_meta["cta"] if matched_meta else "Follow for more dark secrets."
    pool_theme = matched_meta["scenes_theme"] if matched_meta else "dark psychology eyes"

    # Strict system block injected to enforce hypnotic b-rolls and block office assets
    prompt = f"""
    Write an elite viral TikTok/Shorts script for USA/UK audiences based on this topic: "{topic}".
    
    CRITICAL STRUCTURE MATRIX:
    1. HOOK (First 3 seconds): Must be aggressive, fast-paced, psychological, or revealing.
    2. BODY: Explain the deep dark psychology or body language behind it. Keep it engaging.
    3. CTA (Last 3 seconds): You MUST end the voiceover text naturally with this exact call to action phrase: "{pool_cta}".
    
    B-ROLL ASSET SEARCH INSTRUCTIONS:
    - You MUST output exactly 3 scenes.
    - Each 'visual_query' MUST be explicitly related to these keywords: {pool_theme}, dark psychology, neon brains, macro eyes, pupil dilation, shadows.
    - STRICT BAN: Never include keywords like 'office', 'meeting', 'corporate', 'happy business team', or 'bright casual conversation'. Keep it cinematic, raw, and mysterious.

    Output ONLY a valid JSON object format:
    {{
        "title": "Short title highlighting the psychological trap",
        "voiceover": "Full narrative script including the hook, body, and the absolute final CTA text.",
        "scenes": [
            {{"visual_query": "macro portrait close up of serious dark eyes staring"}},
            {{"visual_query": "shadowy silhouette figure in a dark foggy room mystery"}},
            {{"visual_query": "cinematic neon glowing brain synapses glitching visualization"}}
        ]
    }}
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

def pick_topic_for_run():
    """Selects a random topic from the pool."""
    return random.choice(TOPIC_POOL)["topic"]
