"""
script_generator.py — Groq Script & SEO Generation
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────────
Calls the Groq API with a detailed system prompt to produce:
  • A tight 30-59 second narration script
  • Timestamped word-by-word caption data
  • B-roll search keywords
  • Fully optimised SEO JSON (title, description, tags)

All output is returned as a single validated Python dict.
"""

import json
import re
import random
import logging
from tenacity import retry, stop_after_attempt, wait_fixed

from groq import Groq
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# ── Instantiate Groq client once at module level ────────────────────────────
_client = Groq(api_key=config.GROQ_API_KEY)


# ═══════════════════════════════════════════════════════════════════════════════
# TOPIC POOL  — rotated randomly each run to guarantee variety
# ═══════════════════════════════════════════════════════════════════════════════

TOPIC_POOL = [
    "How AI surveillance cameras track your face without consent",
    "The hidden algorithm that decided you didn't get that job",
    "Why ChatGPT sometimes lies with complete confidence",
    "The dark side of AI-generated deepfake voices scamming families",
    "How social media AI is engineered to trigger dopamine addiction",
    "The secret score banks use to predict your financial future",
    "AI that predicts crime before it happens — and gets it wrong",
    "How recommendation algorithms trap you in an echo chamber forever",
    "The company that sells your location data to anyone who pays",
    "Why AI systems trained on biased data make racist decisions",
    "The ghost workers behind every AI model you've ever used",
    "How Google's AI knows your search intent before you finish typing",
    "The AI emotion-detection system used in job interviews",
    "Why AI writing detectors are dangerously inaccurate",
    "The military drones that choose their own targets using AI",
    "How TikTok's algorithm knows your secrets better than your therapist",
    "The psychological manipulation tactics built into every app you use",
    "AI-generated propaganda: how fake news is now indistinguishable",
    "The dark truth about how AI models are trained on stolen art",
    "Why AI hallucinations could get someone killed in a hospital",
]


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = f"""
You are an expert short-form video scriptwriter and SEO strategist specialising in
viral, suspenseful content about AI and technology's dark realities.

NICHE: {config.NICHE_CONTEXT}

CRITICAL RULES:
1. The narration script must be between 110 and 160 words — this maps to 30-59 seconds
   at a natural speaking pace. Never exceed 160 words.
2. Write in second-person ("you", "your") to create urgency and personal connection.
3. Use a HOOK as the very first sentence — make it shocking, counter-intuitive, or
   threatening to grab attention instantly.
4. Language must be clear, punchy, and accessible — no jargon.
5. End with a powerful call-to-action or cliffhanger that begs the viewer to follow.
6. Return ONLY a valid JSON object. No prose outside the JSON. No markdown fences.

REQUIRED JSON SCHEMA (return exactly this structure):
{{
  "topic": "<The specific topic of this video>",
  "script": "<Full narration text, 110-160 words, no newlines inside this string>",
  "broll_keywords": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"],
  "seo": {{
    "title": "<Clickbait title under 60 chars — capitalise key words>",
    "description": "<150-200 word description with hook, keyword-rich content, call to action, and relevant hashtags inline>",
    "hashtags": ["#AITechnology", "#DarkReality", "#MindBlown", "#TechTruths", "#AIFacts"]
  }}
}}

For broll_keywords: choose concrete, visually searchable terms related to the topic
(e.g. "surveillance camera city", "hacker dark room", "data center servers").
For hashtags: include 10 trending tags optimised for YouTube Shorts, Instagram Reels,
and TikTok covering both USA and UK audiences.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

@retry(stop=stop_after_attempt(config.API_RETRY_ATTEMPTS),
       wait=wait_fixed(config.API_RETRY_WAIT_SEC))
def generate_script(topic: str | None = None) -> dict:
    """
    Call Groq and return a validated dict with keys:
        topic, script, broll_keywords, seo {title, description, hashtags}

    Parameters
    ----------
    topic : str | None
        Specific topic override.  If None, one is chosen at random from TOPIC_POOL.
    """
    if topic is None:
        topic = random.choice(TOPIC_POOL)

    logger.info(f"Generating script for topic: '{topic}'")

    user_message = (
        f"Create a complete short-form video package for this topic:\n\n"
        f"TOPIC: {topic}\n\n"
        f"Remember: return ONLY the JSON object, no extra text."
    )

    response = _client.chat.completions.create(
        model=config.GROQ_MODEL,
        max_tokens=config.GROQ_MAX_TOKENS,
        temperature=config.GROQ_TEMPERATURE,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
    )

    raw_text = response.choices[0].message.content.strip()
    logger.info(f"Groq raw response ({len(raw_text)} chars) received.")

    # ── Strip accidental markdown fences if the model disobeys ──────────────
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error(f"JSON parse failure: {exc}\nRaw text:\n{raw_text}")
        raise ValueError(f"Groq returned non-JSON content: {exc}") from exc

    _validate_schema(data)
    logger.info(f"Script generated successfully. Title: '{data['seo']['title']}'")
    return data


def _validate_schema(data: dict) -> None:
    """Raise ValueError if required keys are missing or malformed."""
    required_top = {"topic", "script", "broll_keywords", "seo"}
    required_seo = {"title", "description", "hashtags"}

    missing_top = required_top - set(data.keys())
    if missing_top:
        raise ValueError(f"Missing top-level keys: {missing_top}")

    missing_seo = required_seo - set(data.get("seo", {}).keys())
    if missing_seo:
        raise ValueError(f"Missing seo keys: {missing_seo}")

    if not isinstance(data["broll_keywords"], list) or len(data["broll_keywords"]) < 3:
        raise ValueError("broll_keywords must be a list with at least 3 items.")

    word_count = len(data["script"].split())
    if word_count < 80 or word_count > 180:
        logger.warning(
            f"Script word count ({word_count}) is outside the ideal 110-160 range. "
            "Proceeding anyway."
        )

    title_len = len(data["seo"]["title"])
    if title_len > 100:
        # Truncate gracefully rather than crashing
        data["seo"]["title"] = data["seo"]["title"][:97] + "..."
        logger.warning("Title truncated to 100 characters.")


# ═══════════════════════════════════════════════════════════════════════════════
# WORD-TIMING HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def build_word_timings(script: str, audio_duration: float) -> list[dict]:
    """
    Distribute words evenly across the audio duration.
    Returns a list of dicts: [{word, start, end}, ...]

    In production this is replaced by the word-boundary events that
    edge-tts emits (see audio_generator.py).  This function serves as
    a reliable fallback when those events are unavailable.
    """
    words = script.split()
    if not words:
        return []

    per_word = audio_duration / len(words)
    timings = []
    t = 0.0
    for word in words:
        # Strip punctuation for cleaner caption display
        clean = re.sub(r"[^\w''-]", "", word)
        if clean:
            timings.append({"word": clean, "start": round(t, 3), "end": round(t + per_word, 3)})
        t += per_word
    return timings


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import pprint
    result = generate_script()
    pprint.pprint(result)
