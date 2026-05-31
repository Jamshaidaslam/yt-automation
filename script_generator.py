"""
script_generator.py — Groq Script & SEO Generation (COGNITIVE DARK PSYCHOLOGY)
AI Dark Realities · Short-Form Video Pipeline (ULTRA-FAST INDEXING ENHANCED)
────────────────────────────────────────────────────────────────────────────────────
"""

import json
import re
import random
import logging
import sys
import os

from groq import Groq

try:
    import config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False

GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or (config.GROQ_API_KEY if HAS_CONFIG else None)

if not GROQ_API_KEY:
    raise ValueError('GROQ_API_KEY nahi mili! GitHub Secrets ya config file check karein.')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')

_client = Groq(api_key=GROQ_API_KEY)

# ═══════════════════════════════════════════════════════════════════
# ULTRA-VIRAL TOPIC POOL v3.0 — COGNITIVE DARK SELECTION
# ═══════════════════════════════════════════════════════════════════
TOPIC_POOL = [
    "The Cognitive Dark technique that makes anyone regret leaving you",
    "Psychologists discovered a cognitive bias that makes anyone trust you in 7 seconds",
    "The silent manipulation tactic toxic people use that your subconscious can't detect",
    "How dark triad personalities hijack your brain's neural trust pathways",
    "The reverse psychology trap that forces a liar's brain to confess the truth",
    "What physically happens in your prefrontal cortex when someone gaslights you successfully",
    "The forbidden NLP trick that plants a suggestion into someone's subconscious invisibly",
    "Why highly intelligent brains are easier to cognitively manipulate than average ones",
    "The body language micro-expression that tells you someone is lying right now",
    "How cults use cognitive dissonance to trap highly educated people",
    "Scientists confirmed the exact millisecond your brain decides to trust a stranger",
    "The terrifying psychological reason why empathetic people attract narcissists",
    "Your brain literally erases memories it finds too painful through cognitive shielding",
    "The dark neurological reason you feel empty after getting everything you ever wanted",
    "Why your subconscious mind makes every life decision 7 seconds before you realize it",
    "The psychological phenomenon that makes you fall in love with someone dangerous",
    "What your sleeping position secretly reveals about your dark triad traits",
    "The hidden reason your energy fields feel drained after being around certain people",
    "Why your brain bonds faster with someone who hurt you through trauma-looping",
    "The psychological trick used in every viral ad to hijack your dopamine levels",
    "The terrifying reason your brain generates a full dream in the last 2 minutes of sleep",
    "Scientists still can't explain why the human brain predicts death 7 days early",
    "What physically happens inside your skull when you feel someone watching you",
    "The biological reason eye contact with a stranger triggers a neural panic response",
    "Your body starts dying in a specific sequence and your brain deliberately hides it",
    "The real reason deja vu happens and why it indicates a glitch in memory storage",
    "What your brain chemistry does in the 6 minutes after your heart stops beating",
    "The documented phenomenon where humans develop a defensive split personality under stress",
    "Why your brain sometimes hears your name called when no one is there",
    "The scientific reason certain people can sense danger before it physically happens",
    "The dark psychological reason successful people are hated by their closest friends",
    "How to instantly detect a fake friend using one clinical psychological test",
    "The silent war psychology: what highly secure people never do in arguments",
    "Why people who were humiliated in public become the most dangerous enemies",
    "The psychological reason your enemies smile the widest at your success",
    "What happens to your brain chemistry when someone ignores you on purpose",
    "The dark truth about why genuinely confident people use conversational silence",
    "The psychological reason people sabotage relationships right before they succeed",
    "The unsettling truth about what your recurring nightmare is actually warning you about",
    "Psychology confirms most people are living a life chosen by someone else entirely",
    "The terrifying documented case where a person woke up speaking a foreign language",
    "What happens to your sense of identity when you go completely silent for 72 hours",
    "Psychologists say the version of you that exists at 3AM is your true self",
    "The dark reason highly empathetic people often become emotionally numb over time",
]

# ═══════════════════════════════════════════════════════════════════
# SYSTEM PROMPT v5.0 — FAST ALGORITHM INDEXING FORCE CODES
# ═══════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = (
    "You are an expert elite clinical psychological scriptwriter specializing in Cognitive Dark Psychology and human manipulation. "
    "Your core objective is to write a short-form script that forces an instantaneous 100%+ retention loop. "
    "Target Audience: High-intellect, curious viewers in the USA and United Kingdom.\n\n"

    "ALGORITHM INDEXING CRITERIA (GOLI SPEED FORCE):\n"
    "1. HIGH-OCTANE HOOK: The very first sentence MUST contain an intense, advanced psychological term "
    "(e.g., Cognitive Dark, Dark Triad, Neural Loop, Subconscious Hack, Cognitive Dissonance). This forces "
    "the YouTube OCR and transcript AI to categorize the niche within minutes of uploading.\n"
    "2. GEOGRAPHIC PHRASEOLOGY: Use distinct, clean American/British English vocabulary. Speak like a professional "
    "whispering an intense, dangerous clinical secret. Avoid all generic AI fluff words ('Moreover', 'Furthermore', 'Imagine this', 'In conclusion').\n"
    "3. SCRIPT LENGTH: Strictly between 100 and 120 words. No exceptions. Pacing must be aggressive and direct.\n"
    "4. SEO BLOCK: Keep descriptions extremely tight and punchy (no more than 2 sentences). Use exactly 3-4 viral, niche-specific hashtags.\n\n"
    
    "OUTPUT FORMAT:\n"
    "Return ONLY a valid, clean JSON object. No markdown wrappers, no backticks, no prose.\n"
    "{\n"
    '  "topic": "string",\n'
    '  "script": "string — Under 120 words, raw second-person narrative starting with a heavy terms hook",\n'
    '  "broll_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],\n'
    '  "seo": {\n'
    '    "title": "string under 55 characters with massive curiosity gap",\n'
    '    "description": "string under 50 words forcing rapid semantic indexing",\n'
    '    "hashtags": ["#Shorts", "#DarkPsychology", "#CognitiveDark"]\n'
    '  }\n'
    "}"
)

MODEL_CHAIN = [
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'gemma2-9b-it'
]

def _call_groq(topic: str, model: str) -> dict:
    user_message = (
        f'Generate an elite cognitive psychology short package for this topic:\n\n'
        f'TOPIC: {topic}\n\n'
        f'CRITICAL INDEXING REQS:\n'
        f'— Script word count: 100-120 words strictly.\n'
        f'— Hook must start with high-volume psychological vocabulary.\n'
        f'— Exactly 3 to 4 hashtags in SEO block to completely prevent metadata spam flagging.'
    )
    logger.info(f'Calling Groq model: {model}')
    response = _client.chat.completions.create(
        model=model,
        max_tokens=1000,
        temperature=0.78,  # Optimized for rock-solid JSON extraction
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': user_message}
        ]
    )
    raw_text = response.choices[0].message.content.strip()

    if raw_text.startswith('```'):
        raw_text = re.sub(r'^```[a-zA-Z]*\n?', '', raw_text)
        raw_text = re.sub(r'```$', '', raw_text)
    raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error(f'JSON parse error: {exc}\nRaw:\n{raw_text[:300]}')
        raise ValueError(f'Invalid JSON from Groq: {exc}') from exc
    return data

def generate_script(topic: str | None = None) -> dict:
    if topic is None:
        topic = random.choice(TOPIC_POOL)
    logger.info(f'Selected topic: "{topic}"')

    last_error = None
    for model in MODEL_CHAIN:
        try:
            data = _call_groq(topic, model)
            _validate_and_fix(data)
            _log_quality_check(data)
            logger.info(f'Script generated via {model}')
            return data
        except Exception as exc:
            logger.warning(f'Model {model} failed: {exc}')
            last_error = exc
            continue

    raise RuntimeError(f'All Groq models failed. Last error: {last_error}')

def _validate_and_fix(data: dict) -> None:
    for key in ('topic', 'script', 'broll_keywords', 'seo'):
        if key not in data:
            data[key] = 'Missing data'

    seo = data.get('seo', {})
    if not isinstance(seo, dict):
        data['seo'] = seo = {}
    for key in ('title', 'description', 'hashtags'):
        if key not in seo:
            seo[key] = 'Missing seo data'

    if not isinstance(data['broll_keywords'], list):
        data['broll_keywords'] = [
            'dark psychology aesthetic cinematic',
            'mysterious shadow manipulation',
            'brain synapse activity abstract',
            'human macro eye staring thriller'
        ]
    if len(data['broll_keywords']) < 4:
        defaults = ['dark mind corridor 4K', 'psychological shadow manipulation', 'human brain scanning', 'closeup cold eyes']
        data['broll_keywords'].extend(defaults[:4 - len(data['broll_keywords'])])

    if isinstance(seo.get('title'), str) and len(seo['title']) > 60:
        seo['title'] = seo['title'][:52] + '...'

    # Forced strict tags to instantly map USA/UK feeds without triggering meta-spam blocks
    if not isinstance(seo.get('hashtags'), list) or len(seo['hashtags']) > 4:
        seo['hashtags'] = ['#Shorts', '#DarkPsychology', '#CognitiveDark']

def _log_quality_check(data: dict) -> None:
    script = data.get('script', '')
    word_count = len(script.split())
    has_you = 'you' in script.lower()
    title_len = len(data.get('seo', {}).get('title', ''))

    logger.info(f'  Word count : {word_count} (target: 100-120)')
    logger.info(f'  Uses "you" : {has_you}')
    logger.info(f'  Title len  : {title_len} chars (limit: 60)')

def build_word_timings(script: str, audio_duration: float) -> list[dict]:
    words = script.split()
    if not words:
        return []
    per_word = audio_duration / len(words)
    timings = []
    t = 0.0
    for word in words:
        clean = ''.join(c for c in word if c.isalnum() or c in "'-")
        if clean:
            timings.append({
                'word':  clean,
                'start': round(t, 3),
                'end':   round(t + per_word, 3)
            })
        t += per_word
    return timings

if __name__ == '__main__':
    import pprint
    print('\n' + '=' * 60)
    print('  GOLI SPEED COGNITIVE INDEXING ENGINE ACTIVE')
    print('  AI Dark Realities · Short-Form Pipeline v3.0')
    print('=' * 60 + '\n')
    result = generate_script()
    pprint.pprint(result, width=80)
