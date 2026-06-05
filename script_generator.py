"""
script_generator.py — VIRAL DOMINATION ENGINE v3.0
"""
import json
import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 120 VIRAL TOPIC POOL
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
    Uses Groq AI to generate a viral script based on the hook formula.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    prompt = f"""
    Write a viral TikTok/Shorts script for this topic: "{topic}".
    Follow this structure:
    1. HOOK (First 3 seconds): Must be aggressive, controversial, or revealing.
    2. BODY: Explain the psychology behind it, fast-paced.
    3. CTA (Last 3 seconds): Force a specific action.
    Keep it under 60 seconds. Output as JSON: {{"title": "...", "voiceover": "...", "visual_queries": ["...", "..."]}}
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
    
import random

    def pick_topic_for_run():
    """Selects a random topic from the pool."""
    # Direct access, no need to re-import
    return random.choice(TOPIC_POOL)["topic"]
