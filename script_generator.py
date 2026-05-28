"""
script_generator.py — Groq Script & SEO Generation
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────────
Fixed:
  - Model changed to llama-3.3-70b-versatile (current valid Groq model)
  - BadRequestError caught and logged with full detail before retry
  - response_format json_object enforced so model never wraps in markdown
  - max_tokens raised to 1500 to avoid truncated JSON
  - GitHub Actions compatibility added for GROQ_API_KEY
  - Fixed syntax error in build_word_timings (line breaking bug solved)
"""

import json
import re
import random
import logging
import sys
import os  # <-- Environment variables read karne k liye zaroori hai
from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log

from groq import Groq, BadRequestError

# ── GITHUB ACTIONS OR LOCAL CONFIG LAYER ──────────────────────────────────────
try:
    import config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False

# Pehle GitHub Secrets/Environment check karega, agar wahan na ho to config file se uthayegi
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or (config.GROQ_API_KEY if HAS_CONFIG else None)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY nahi mili! GitHub Secrets ya config file check karein.")
# ─────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# ── Groq client ──────────────────────────────────────────────────────────────
_client = Groq(api_key=GROQ_API_KEY)


# ═══════════════════════════════════════════════════════════════════════════════
# TOPIC POOL
# ═══════════════════════════════════════════════════════════════════════════════

TOPIC_POOL = [
    "How AI surveillance cameras track your face without consent",
    "The hidden algorithm that decided you didn't get that job",
    "Why ChatGPT sometimes lies with complete confidence",
    "The dark side of AI-generated deepfake voices scamming families",
    "How social media AI is engineered to trigger dopamine addiction",
    "The secret score banks use to predict your financial future",
    "AI that predicts crime before it happens and gets it wrong",
    "How recommendation algorithms trap you in an echo chamber forever",
    "The company that sells your location data to anyone who pays",
    "Why AI systems trained on biased data make racist decisions",
    "The ghost workers behind every AI model you have ever used",
    "How Google AI knows your search intent before you finish typing",
    "The AI emotion-detection system used in job interviews",
    "Why AI writing detectors are dangerously inaccurate",
    "The military drones that choose their own targets using AI",
    "How TikTok algorithm knows your secrets better than your therapist",
    "The psychological manipulation tactics built into every app you use",
    "AI-generated propaganda and how fake news is now indistinguishable",
    "The dark truth about how AI models are trained on stolen art",
    "Why AI hallucinations could get someone killed in a hospital",
]


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are an expert short-form video scriptwriter and SEO strategist
specialising in viral, suspenseful content about AI and technology dark realities.
Target audience: curious adults aged 18-45 in the USA and UK.

RULES:
1. Script must be 110 to 150 words total. No more, no less.
2. Write in second-person using you and your to create urgency.
3. First sentence must be a shocking hook.
4. End with a call-to-action asking viewers to follow for more.
5. Return ONLY a valid JSON object matching the exact schema below.
6. Do NOT include any text outside the JSON object.
7. Do NOT use markdown code fences.

EXACT JSON SCHEMA TO RETURN:
{
  "topic": "string",
  "script": "string with 110 to 150 words",
  "broll_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "seo": {
    "title": "string under 60 characters",
    "description": "string 150 to 200 words packed with keywords",
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6", "#tag7", "#tag8", "#tag9", "#tag10"]
  }
}"""


# ═══════════════════════════════════════════════════════════════════════════════
# AVAILABLE GROQ MODELS (fallback chain if primary fails)
# ═══════════════════════════════════════════════════════════════════════════════

MODEL_CHAIN = [
    "llama-3.3-70b-versatile",    # Primary — best quality, current
    "llama-3.1-8b-instant",       # Fallback — faster, smaller
    "gemma2-9b-it",               # Second fallback
]


# ═══════════════════════════════════════════════════════════════════════════════
# CORE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def _call_groq(topic: str, model: str) -> dict:
    """
    Single attempt to call Groq with a specific model.
    Raises BadRequestError or ValueError on failure.
    """
    user_message = (
        f"Create a complete short-form video package for this topic:\n"
        f"TOPIC: {topic}\n"
        f"Return ONLY the JSON object. No extra text. No markdown."
    )

    logger.info(f"Calling Groq model: {model}")

    response = _client.chat.completions.create(
        model=model,
        max_tokens=1500,
        temperature=0.8,
        response_format={"type": "json_object"},   # Forces pure JSON output
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
    )

    raw_text = response.choices[0].message.content.strip()
    logger.info(f"Response received: {len(raw_text)} chars")

    # Safety strip in case model still adds fences
    raw_text = re.sub(r"^
http://googleusercontent.com/immersive_entry_chip/0

Isko paste karke **Commit changes** kar dein aur workflow run karke dekhein!
