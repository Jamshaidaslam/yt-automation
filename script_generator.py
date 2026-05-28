"""
script_generator.py — Groq Script & SEO Generation
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────────
Fixed:
  - Model changed to llama-3.3-70b-versatile (current valid Groq model)
  - BadRequestError caught and logged with full detail before retry
  - response_format json_object enforced so model never wraps in markdown
  - max_tokens raised to 1500 to avoid truncated JSON
"""

import json
import re
import random
import logging
from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log

from groq import Groq, BadRequestError
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# ── Groq client ──────────────────────────────────────────────────────────────
_client = Groq(api_key=config.GROQ_API_KEY)


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
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```\s*$", "", raw_text).strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error(f"JSON parse error: {exc}")
        logger.error(f"Raw text was:\n{raw_text[:500]}")
        raise ValueError(f"Invalid JSON from Groq: {exc}") from exc

    return data


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=False,          # Don't re-raise — we handle via model chain below
)
def _call_groq_with_retry(topic: str, model: str) -> dict:
    return _call_groq(topic, model)


def generate_script(topic: str | None = None) -> dict:
    """
    Generate script + SEO data via Groq.
    Tries each model in MODEL_CHAIN until one succeeds.
    Returns validated dict: {topic, script, broll_keywords, seo}
    """
    if topic is None:
        topic = random.choice(TOPIC_POOL)

    logger.info(f"Generating script — topic: '{topic}'")

    last_error = None
    for model in MODEL_CHAIN:
        try:
            data = _call_groq_with_retry(topic, model)
            _validate_and_fix(data)
            logger.info(f"Script OK via {model} | Title: {data['seo']['title']}")
            return data
        except Exception as exc:
            logger.warning(f"Model {model} failed: {type(exc).__name__}: {exc}")
            last_error = exc
            continue

    # All models failed
    raise RuntimeError(
        f"All Groq models failed for topic '{topic}'. "
        f"Last error: {last_error}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION + AUTO-FIX
# ═══════════════════════════════════════════════════════════════════════════════

def _validate_and_fix(data: dict) -> None:
    """
    Validate schema and auto-fix minor issues instead of crashing.
    Raises ValueError only on unrecoverable problems.
    """
    # ── Top-level keys ───────────────────────────────────────────────────────
    for key in ("topic", "script", "broll_keywords", "seo"):
        if key not in data:
            raise ValueError(f"Missing required key: '{key}'")

    # ── SEO sub-keys ─────────────────────────────────────────────────────────
    seo = data.get("seo", {})
    for key in ("title", "description", "hashtags"):
        if key not in seo:
            raise ValueError(f"Missing seo.{key}")

    # ── broll_keywords must be a list ────────────────────────────────────────
    if not isinstance(data["broll_keywords"], list):
        data["broll_keywords"] = [str(data["broll_keywords"])]
    if len(data["broll_keywords"]) < 3:
        # Pad with generic fallback keywords
        data["broll_keywords"] += [
            "artificial intelligence technology",
            "data privacy surveillance",
            "digital world abstract",
        ]
        data["broll_keywords"] = data["broll_keywords"][:5]

    # ── Title length ─────────────────────────────────────────────────────────
    if len(seo["title"]) > 100:
        seo["title"] = seo["title"][:97] + "..."

    # ── Hashtags must be a list ───────────────────────────────────────────────
    if not isinstance(seo["hashtags"], list):
        seo["hashtags"] = ["#AIFacts", "#DarkReality", "#TechTruths", "#AITechnology", "#Shorts"]

    # ── Script word count warning ─────────────────────────────────────────────
    wc = len(data["script"].split())
    if wc < 80:
        logger.warning(f"Script only {wc} words — may produce a very short video.")
    elif wc > 200:
        logger.warning(f"Script is {wc} words — may exceed 59s. Trimming.")
        words = data["script"].split()[:170]
        data["script"] = " ".join(words)


# ═══════════════════════════════════════════════════════════════════════════════
# WORD TIMING FALLBACK
# ═══════════════════════════════════════════════════════════════════════════════

def build_word_timings(script: str, audio_duration: float) -> list[dict]:
    """Even-distribution word timing fallback when edge-tts events unavailable."""
    words = script.split()
    if not words:
        return []
    per_word = audio_duration / len(words)
    timings  = []
    t = 0.0
    for word in words:
        clean = re.sub(r"[^\w''-]", "", word)
        if clean:
            timings.append({
                "word":  clean,
                "start": round(t, 3),
                "end":   round(t + per_word, 3),
            })
        t += per_word
    return timings


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import pprint
    result = generate_script()
    pprint.pprint(result)
