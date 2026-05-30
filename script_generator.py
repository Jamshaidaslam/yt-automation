"""
script_generator.py — Groq Script & SEO Generation (DARK PSYCHOLOGY & BRAIN MYSTERIES)
AI Dark Realities · Short-Form Video Pipeline
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
# ULTRA-VIRAL TOPIC POOL v2.5 — MAXIMUM HUMAN EMOTION HOOKS
# ═══════════════════════════════════════════════════════════════════
TOPIC_POOL = [
    "The one sentence a narcissist uses right before they destroy you",
    "Psychologists discovered a trick that makes anyone trust you in 7 seconds",
    "The silent manipulation tactic toxic people use that you can't even detect",
    "How dark triad personalities choose their victims — you may already be targeted",
    "The reverse psychology trap that forces someone to confess the truth",
    "What happens in your brain the moment someone gaslights you successfully",
    "The forbidden NLP trick that plants a thought into someone's mind invisibly",
    "Why highly intelligent people are easier to manipulate than average ones",
    "The body language micro-signal that tells you someone is lying right now",
    "How cults use a single psychological technique to trap educated people",
    "Scientists confirmed the exact moment your brain decides to trust a stranger",
    "The terrifying psychological reason why kind people attract abusers",
    "Your brain literally erases memories it finds too painful — here's which ones",
    "The dark reason you feel empty after getting everything you ever wanted",
    "Why your subconscious mind has already made every decision before you do",
    "The psychological phenomenon that makes you fall in love with someone dangerous",
    "What your sleeping position secretly reveals about your hidden personality",
    "The hidden reason you feel drained after being around certain people",
    "Why your brain bonds faster with someone who hurt you than someone who helped",
    "The psychological trick used in every viral ad to make you spend money instantly",
    "The terrifying reason your brain generates a full dream in the last 2 minutes of sleep",
    "Scientists still can't explain why the human brain can predict death 7 days early",
    "What physically happens inside your skull when you feel someone watching you",
    "The biological reason eye contact with a stranger can trigger a panic response",
    "Your body starts dying in a specific sequence — and your brain hides it from you",
    "The real reason deja vu happens — and why it should terrify you",
    "What your brain does in the 6 minutes after your heart stops beating",
    "The documented phenomenon where humans develop a second personality under stress",
    "Why your brain sometimes hears your name called when no one is there",
    "The scientific reason certain people can sense danger before it happens",
    "The dark psychological reason successful people are hated by their closest friends",
    "How to instantly detect a fake friend using one simple psychological test",
    "The silent war psychology: what highly secure people never do in arguments",
    "Why people who were humiliated in public become the most dangerous enemies",
    "The psychological reason your enemies smile the widest at your success",
    "What happens to your brain chemistry when someone ignores you on purpose",
    "The dark truth about why genuinely confident people speak less",
    "The psychological reason people sabotage relationships right before they succeed",
    "The unsettling truth about what your recurring nightmare is actually warning you about",
    "Psychology confirms most people are living a life chosen by someone else entirely",
    "The terrifying documented case where a person woke up speaking a foreign language",
    "What happens to your sense of identity when you go completely silent for 72 hours",
    "Psychologists say the version of you that exists at 3AM is your true self",
    "The dark reason highly empathetic people often become emotionally numb over time",
]

# ═══════════════════════════════════════════════════════════════════
# SYSTEM PROMPT v4.0 — ANTI-SPAM & MAXIMUM RETENTION CODES
# ═══════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = (
    "You are an elite short-form video scriptwriter specializing in Dark Psychology and Human Behavior. "
    "Your goal is to write a script that forces a 100%+ retention rate on YouTube Shorts and Instagram Reels. "
    "Target Audience: Mature, curious individuals in the USA and UK who love mysteries.\n\n"

    "CRITICAL INPUT CRITERIA:\n"
    "1. SCRIPT LENGTH: Strictly between 100 and 125 words. Too long will kill the loop pacing.\n"
    "2. THE HOOK: The first sentence must be short, punchy, and make the viewer feel exposed. No pleasantries.\n"
    "3. HUMAN LANGUAGE: Avoid generic AI transitions like 'Moreover', 'Furthermore', 'In conclusion'. Speak like a real human whispering an unsettling secret.\n"
    "4. SEO OPTIMIZATION: Keep descriptions short (2-3 sentences), highly engaging, and use exactly 3-4 viral hashtags. Do NOT overload tags, as YouTube flags it as metadata spam.\n\n"
    
    "OUTPUT FORMAT:\n"
    "Return ONLY a clean JSON object. No markdown code blocks, no extra text.\n"
    "{\n"
    '  "topic": "string",\n'
    '  "script": "string — Under 125 words, high pacing second-person narrative",\n'
    '  "broll_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],\n'
    '  "seo": {\n'
    '    "title": "string under 55 characters with high curiosity gap",\n'
    '    "description": "string around 60-80 words, natural description that hooks readers",\n'
    '    "hashtags": ["#Shorts", "#DarkPsychology", "#PsychologyFacts"]\n'
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
        f'Generate a complete dark psychology short-form video package for this topic:\n\n'
        f'TOPIC: {topic}\n\n'
        f'CRITICAL:\n'
        f'— Script word count: 100-125 words strictly.\n'
        f'— Maximum 3 to 4 hashtags in SEO block to prevent YouTube spam flagging.\n'
        f'— Make the language gritty, raw, and highly human.'
    )
    logger.info(f'Calling Groq model: {model}')
    response = _client.chat.completions.create(
        model=model,
        max_tokens=1000,
        temperature=0.82,  # Slightly lower temperature for better JSON compliance
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
            'dark aesthetic cinematic',
            'mysterious silhouette shadow',
            'brain neural activity glow',
            'eye close-up macro thriller'
        ]
    if len(data['broll_keywords']) < 4:
        defaults = ['dark corridor 4K', 'psychological thriller shadow', 'human brain scan', 'closeup eye fear']
        data['broll_keywords'].extend(defaults[:4 - len(data['broll_keywords'])])

    if isinstance(seo.get('title'), str) and len(seo['title']) > 60:
        seo['title'] = seo['title'][:55] + '...'

    # Fixed hashtags structure to avoid overload spam
    if not isinstance(seo.get('hashtags'), list) or len(seo['hashtags']) > 4:
        seo['hashtags'] = ['#Shorts', '#DarkPsychology', '#PsychologyFacts']

def _log_quality_check(data: dict) -> None:
    script = data.get('script', '')
    word_count = len(script.split())
    has_you = 'you' in script.lower()
    title_len = len(data.get('seo', {}).get('title', ''))

    logger.info(f'  Word count : {word_count} (target: 100-125)')
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
    print('  ANTI-SPAM DARK PSYCHOLOGY GENERATOR')
    print('  AI Dark Realities · Short-Form Pipeline v2.5')
    print('=' * 60 + '\n')
    result = generate_script()
    pprint.pprint(result, width=80)
