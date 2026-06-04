"""
script_generator.py — Script Generator (GROQ LLAMA3.3-70B)
"""

import json
import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)


def generate_script(topic: str) -> dict:
    logger.info(f"🧠 Generating script for: [{topic}]")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=api_key)

    system_prompt = """
You are a short-form video script writer for YouTube Shorts (35-55 seconds).

STRICT RULES:
1. Hook: 4-6 words max. Punchy opener.
2. Scene 2: text_segment must be "... WAIT. ..." (2s silence beat).
3. Body: Short punchy sentences (4-5 words per scene).
4. Final sentence flows back into the hook (loop structure).
5. Total voiceover must read in 35-55 seconds (roughly 90-140 words).

OUTPUT: Return ONLY a raw JSON object. No markdown. No backticks. No explanation.

SCHEMA:
{
  "title": "Video title for YouTube",
  "voiceover": "Full script text as single string",
  "scenes": [
    {"text_segment": "...", "visual_query": "short stock footage search term"},
    {"text_segment": "... WAIT. ...", "visual_query": "dark dramatic pause closeup"}
  ]
}
"""

    user_prompt = f"Topic: {topic}. Write the script now."

    # BUG FIX 1: No retry logic — if API fails, pipeline crashes silently.
    # Added retry with clear error per attempt.
    last_error = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.6,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            if not raw:
                raise ValueError("Empty response from Groq API.")

            # Strip markdown just in case model ignores instruction
            content = raw.replace("```json", "").replace("```", "").strip()
            data    = json.loads(content)

            # BUG FIX 2: No validation — missing keys cause KeyError crashes
            # downstream in main.py and video_compiler.py
            data = _validate_and_fix(data, topic)

            logger.info(f"✅ Script ready — {len(data['voiceover'].split())} words, "
                        f"{len(data['scenes'])} scenes, "
                        f"{len(data['visual_queries'])} visual queries")
            return data

        except Exception as e:
            last_error = e
            logger.warning(f"Script generation attempt {attempt + 1} failed: {e}")

    raise RuntimeError(f"Script generation failed after 3 attempts. Last error: {last_error}")


# ══════════════════════════════════════════════════════════════════════════════
def _validate_and_fix(data: dict, topic: str) -> dict:
    """
    Ensure all required keys exist with sensible fallbacks.
    Extracts visual_queries list from scenes (used by media_fetcher).
    """

    # BUG FIX 3: 'visual_queries' key never existed in returned dict —
    # main.py does script_data.get("visual_queries") which always returned
    # the hardcoded fallback list, ignoring actual scene queries entirely.
    scenes = data.get("scenes", [])

    # Extract unique visual queries from scenes
    visual_queries = []
    seen = set()
    for scene in scenes:
        vq = scene.get("visual_query", "").strip()
        if vq and vq not in seen:
            visual_queries.append(vq)
            seen.add(vq)

    # Fallback if scenes had no visual_query fields
    if not visual_queries:
        visual_queries = [topic, "dark dramatic atmosphere", "person thinking closeup"]

    # Ensure voiceover exists
    if not data.get("voiceover"):
        # Build voiceover from scene text_segments as fallback
        segments = [s.get("text_segment", "") for s in scenes if s.get("text_segment")]
        data["voiceover"] = " ".join(segments) if segments else topic

    # Ensure title exists
    if not data.get("title"):
        data["title"] = topic

    # Attach visual_queries to returned dict
    data["visual_queries"] = visual_queries

    # Warn if voiceover seems too short or too long
    word_count = len(data["voiceover"].split())
    if word_count < 60:
        logger.warning(f"⚠️  Voiceover may be too short: {word_count} words (target: 90-140)")
    elif word_count > 160:
        logger.warning(f"⚠️  Voiceover may be too long: {word_count} words (target: 90-140)")

    return data
