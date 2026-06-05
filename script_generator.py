"""
script_generator.py — VIRAL DOMINATION ENGINE v3.0
AI Dark Realities · USA/UK 10M Traffic System
═══════════════════════════════════════════════════════════════════════════════

WHAT MAKES THIS 1000x BETTER:

1. NICHE CATEGORIES — 6 proven viral categories instead of generic "dark psychology"
   Body Language · Eye Reading · Confidence · Attraction Psychology ·
   Mind Control · Human Behavior Secrets

2. HOOK FORMULA ENFORCED — Every script starts with a proven viral hook pattern:
   "If someone does X — it means Y"  ← Curiosity gap (highest CTR)
   "Most people never notice this"   ← Exclusivity trigger
   "Stop doing X right now"          ← Direct threat/urgency
   "This one thing reveals everything about someone" ← Revelation hook

3. PERSONAL & RELATABLE — Scripts written so viewer thinks:
   "This is literally about me" → Share rate skyrockets

4. CTA SYSTEM — Every video ends with:
   Save + Follow + Part teaser → Forces algorithm to push the video

5. SERIES FORMAT — Topics auto-generate as Part 1/2/3 series
   → Each part pulls audience from previous → Compounding growth

6. THUMBNAIL LINE — First sentence = thumbnail text
   Bold claim that stops the scroll

7. 120 VIRAL TOPICS across 6 categories — 40 days of unique content at 3/day
   Body language, eye secrets, confidence signals, attraction cues,
   manipulation detection, human behavior reading

8. PSYCHOLOGICAL TRIGGERS in every script:
   - Identity threat ("you're doing this wrong")
   - Curiosity gap ("here's what it really means")
   - Social proof ("people who know this...")
   - FOMO ("most people never find out")
"""

import json
import os
import re
import logging
from datetime import datetime
from groq import Groq

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 120 VIRAL TOPIC POOL — 6 Categories × 20 Topics
# These are NOT generic — each one is a specific shareable insight
# ═══════════════════════════════════════════════════════════════════════════════

TOPIC_POOL = [

    # ── CATEGORY 1: Eye Reading & Secrets (most viral) ────────────────────────
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

    # ── CATEGORY 2: Body Language Reading ─────────────────────────────────────
    {
        "topic": "The way someone positions their feet tells you exactly where their mind is",
        "category": "body_language",
        "hook_type": "revelation",
        "series": "Body Secrets", "part": 1,
        "cta": "Save this — look at feet in every conversation",
        "scenes_theme": "feet direction, body orientation, standing posture, subtle body cues"
    },
    {
        "topic": "When someone mirrors your body language — your brain already knows what it means",
        "category": "body_language",
        "hook_type": "curiosity_gap",
        "series": "Body Secrets", "part": 2,
        "cta": "Comment if someone is mirroring you right now",
        "scenes_theme": "mirroring body language, synchronized movement, conversation body, attraction signal"
    },
    {
        "topic": "Touching the neck means one thing — and it reveals everything about how they feel",
        "category": "body_language",
        "hook_type": "revelation",
        "series": "Body Secrets", "part": 3,
        "cta": "Follow for Part 4 — the hands reveal even more",
        "scenes_theme": "neck touch gesture, stress signal, self soothing, nervous body language"
    },
    {
        "topic": "The hand gesture that shows someone is lying directly to your face",
        "category": "body_language",
        "hook_type": "identity_threat",
        "series": "Body Secrets", "part": 4,
        "cta": "Save this — you'll catch it this week",
        "scenes_theme": "hand covering mouth, face touching, deception gesture, nervous hands"
    },
    {
        "topic": "How someone holds their coffee cup tells you their entire personality",
        "category": "body_language",
        "hook_type": "curiosity_gap",
        "series": "Body Secrets", "part": 5,
        "cta": "Comment your cup style below",
        "scenes_theme": "coffee cup holding, hand grip, personality body language, casual gesture"
    },
    {
        "topic": "The subtle lean — when someone's body says yes before their mouth does",
        "category": "body_language",
        "hook_type": "revelation",
        "series": "Body Secrets", "part": 6,
        "cta": "Save this and watch people lean today",
        "scenes_theme": "body lean forward, interest signal, engaged conversation, subtle attraction"
    },
    {
        "topic": "Crossed arms do NOT mean what you think — here is the real signal",
        "category": "body_language",
        "hook_type": "myth_bust",
        "series": "Body Secrets", "part": 7,
        "cta": "Follow — everything you knew is wrong",
        "scenes_theme": "crossed arms portrait, defensive posture, comfort body language, self hug"
    },
    {
        "topic": "The space someone keeps from you reveals exactly how they feel about you",
        "category": "body_language",
        "hook_type": "curiosity_gap",
        "series": "Body Secrets", "part": 8,
        "cta": "Save this — measure the distance next time",
        "scenes_theme": "personal space distance, proximity attraction, close conversation, physical space"
    },
    {
        "topic": "If someone does THIS with their hands when you talk — they find you fascinating",
        "category": "body_language",
        "hook_type": "revelation",
        "series": "Body Secrets", "part": 9,
        "cta": "Comment below — does someone do this to you",
        "scenes_theme": "hand steeple gesture, open palms, engaged hands, interested body language"
    },
    {
        "topic": "The single most powerful body language move that commands instant respect",
        "category": "body_language",
        "hook_type": "power_secret",
        "series": "Body Secrets", "part": 10,
        "cta": "Save this — use it in your next meeting",
        "scenes_theme": "power posture, confident stance, wide stance portrait, authority body language"
    },

    # ── CATEGORY 3: Confidence & Presence ─────────────────────────────────────
    {
        "topic": "The voice tone that makes people stop and listen — you can learn it in one day",
        "category": "confidence",
        "hook_type": "power_secret",
        "series": "Confidence Code", "part": 1,
        "cta": "Save this and practice tonight",
        "scenes_theme": "confident speaking, strong voice, command presence, microphone close"
    },
    {
        "topic": "Walking into a room THIS way makes everyone unconsciously respect you",
        "category": "confidence",
        "hook_type": "power_secret",
        "series": "Confidence Code", "part": 2,
        "cta": "Follow — Part 3 is the eye contact secret",
        "scenes_theme": "confident walk, entering room, head high posture, commanding entrance"
    },
    {
        "topic": "The pause — why the most powerful people say nothing and control everything",
        "category": "confidence",
        "hook_type": "curiosity_gap",
        "series": "Confidence Code", "part": 3,
        "cta": "Save this — silence is your weapon",
        "scenes_theme": "deliberate pause, thinking silence, powerful stillness, calm confident face"
    },
    {
        "topic": "Why you lose respect the moment you start explaining yourself to people",
        "category": "confidence",
        "hook_type": "identity_threat",
        "series": "Confidence Code", "part": 4,
        "cta": "Comment if you do this — most people do",
        "scenes_theme": "over explaining, self justifying, shrinking body language, approval seeking"
    },
    {
        "topic": "The handshake secret that instantly tells someone you are not to be messed with",
        "category": "confidence",
        "hook_type": "power_secret",
        "series": "Confidence Code", "part": 5,
        "cta": "Save this before your next handshake",
        "scenes_theme": "firm handshake, confident grip, eye contact handshake, power greeting"
    },
    {
        "topic": "How to make your presence felt before you even speak a single word",
        "category": "confidence",
        "hook_type": "power_secret",
        "series": "Confidence Code", "part": 6,
        "cta": "Follow — this series will change your life",
        "scenes_theme": "silent presence, commanding stillness, room energy, charismatic aura"
    },
    {
        "topic": "Saying NO without explanation is the most powerful thing you will ever do",
        "category": "confidence",
        "hook_type": "identity_threat",
        "series": "Confidence Code", "part": 7,
        "cta": "Save this and say no today — no reason",
        "scenes_theme": "firm no gesture, boundary setting, confident refusal, self respect"
    },
    {
        "topic": "The slow blink — why powerful people never look rushed or reactive",
        "category": "confidence",
        "hook_type": "curiosity_gap",
        "series": "Confidence Code", "part": 8,
        "cta": "Follow — tomorrow is even more powerful",
        "scenes_theme": "slow deliberate movement, unrushed confidence, calm under pressure, composed face"
    },
    {
        "topic": "Your posture right now is telling everyone around you how to treat you",
        "category": "confidence",
        "hook_type": "identity_threat",
        "series": "Confidence Code", "part": 9,
        "cta": "Comment — sit up straight after watching this",
        "scenes_theme": "slouch vs upright posture, spine alignment, confident sitting, body signal"
    },
    {
        "topic": "The 60 second morning routine that rewires your brain for dominance all day",
        "category": "confidence",
        "hook_type": "power_secret",
        "series": "Confidence Code", "part": 10,
        "cta": "Save this — do it tomorrow morning",
        "scenes_theme": "morning ritual, power pose, confident start, morning determination face"
    },

    # ── CATEGORY 4: Attraction & Connection Psychology ─────────────────────────
    {
        "topic": "If someone remembers small details you said weeks ago — this is what it means",
        "category": "attraction",
        "hook_type": "revelation",
        "series": "Attraction Secrets", "part": 1,
        "cta": "Save this — someone is doing this to you right now",
        "scenes_theme": "memory detail, thoughtful remembering, caring attention, emotional recall"
    },
    {
        "topic": "The psychological reason someone can not stop thinking about you after one meeting",
        "category": "attraction",
        "hook_type": "curiosity_gap",
        "series": "Attraction Secrets", "part": 2,
        "cta": "Follow for Part 3 — how to trigger this on purpose",
        "scenes_theme": "thinking of someone, obsessive thought, distracted person, haunted by memory"
    },
    {
        "topic": "How to make someone feel like they have known you for years in under 10 minutes",
        "category": "attraction",
        "hook_type": "power_secret",
        "series": "Attraction Secrets", "part": 3,
        "cta": "Save this — it works on anyone",
        "scenes_theme": "instant connection, warm conversation, deep rapport, trusting face"
    },
    {
        "topic": "The question that makes anyone open up emotionally — use it carefully",
        "category": "attraction",
        "hook_type": "power_secret",
        "series": "Attraction Secrets", "part": 4,
        "cta": "Follow — tomorrow is the touch psychology secret",
        "scenes_theme": "deep conversation, emotional opening, vulnerability face, intimate talk"
    },
    {
        "topic": "When someone texts you back immediately — your brain does something you don't control",
        "category": "attraction",
        "hook_type": "curiosity_gap",
        "series": "Attraction Secrets", "part": 5,
        "cta": "Comment if your heart jumped reading this",
        "scenes_theme": "phone notification, excited text response, phone smile, message anticipation"
    },
    {
        "topic": "The psychological trick behind why playing hard to get actually works on the brain",
        "category": "attraction",
        "hook_type": "revelation",
        "series": "Attraction Secrets", "part": 6,
        "cta": "Save this — understand your own brain",
        "scenes_theme": "withdrawal psychology, chase instinct, wanting what pulls away, desire brain"
    },
    {
        "topic": "How to make someone feel like YOU are the most interesting person they have ever met",
        "category": "attraction",
        "hook_type": "power_secret",
        "series": "Attraction Secrets", "part": 7,
        "cta": "Follow — this one conversation skill changes everything",
        "scenes_theme": "fascinated listener, engaged face, deeply interested person, captivated eyes"
    },
    {
        "topic": "The light touch on the arm and what your nervous system does in 0.3 seconds",
        "category": "attraction",
        "hook_type": "curiosity_gap",
        "series": "Attraction Secrets", "part": 8,
        "cta": "Save this — your body already knew",
        "scenes_theme": "arm touch, skin contact reaction, nervous system, subtle physical touch"
    },
    {
        "topic": "Why the person who cares less always has more power in every relationship",
        "category": "attraction",
        "hook_type": "identity_threat",
        "series": "Attraction Secrets", "part": 9,
        "cta": "Comment if you are always the one who cares more",
        "scenes_theme": "power imbalance relationship, emotional investment, detachment power, caring less"
    },
    {
        "topic": "The silence between two people that says more than any words ever could",
        "category": "attraction",
        "hook_type": "revelation",
        "series": "Attraction Secrets", "part": 10,
        "cta": "Follow — the next video will feel personal",
        "scenes_theme": "comfortable silence, two people, unspoken connection, quiet intimacy portrait"
    },

    # ── CATEGORY 5: Reading People & Lie Detection ─────────────────────────────
    {
        "topic": "The 3 second reaction that reveals someone's true feelings before they can fake it",
        "category": "people_reading",
        "hook_type": "revelation",
        "series": "Read Anyone", "part": 1,
        "cta": "Save this — you will see it everywhere now",
        "scenes_theme": "micro expression, split second reaction, genuine vs fake face, true feeling"
    },
    {
        "topic": "How to know someone is fake nice — the one sign that never lies",
        "category": "people_reading",
        "hook_type": "identity_threat",
        "series": "Read Anyone", "part": 2,
        "cta": "Follow for Part 3 — how to spot fake loyalty",
        "scenes_theme": "fake smile, eyes not smiling, performative kindness, two faced person"
    },
    {
        "topic": "If someone laughs before answering your question — your gut is right about them",
        "category": "people_reading",
        "hook_type": "curiosity_gap",
        "series": "Read Anyone", "part": 3,
        "cta": "Save this and watch for it this week",
        "scenes_theme": "nervous laugh, deflecting humor, uncomfortable smile, evasive person"
    },
    {
        "topic": "The word people who are lying always use — and they never know they are doing it",
        "category": "people_reading",
        "hook_type": "revelation",
        "series": "Read Anyone", "part": 4,
        "cta": "Comment the word below — see who knows",
        "scenes_theme": "verbal lie, speech pattern, word choice, conversation analysis, deception talk"
    },
    {
        "topic": "Why people who talk too much about loyalty are usually the least loyal",
        "category": "people_reading",
        "hook_type": "identity_threat",
        "series": "Read Anyone", "part": 5,
        "cta": "Save this — think of someone right now",
        "scenes_theme": "performative loyalty, loud declarations, overcompensation, trust betrayal"
    },
    {
        "topic": "The question that instantly reveals someone's true character in 10 seconds",
        "category": "people_reading",
        "hook_type": "power_secret",
        "series": "Read Anyone", "part": 6,
        "
