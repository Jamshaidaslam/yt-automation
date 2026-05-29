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

# GitHub Secrets ya local config se API Key uthane ka setup
GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or (config.GROQ_API_KEY if HAS_CONFIG else None)

if not GROQ_API_KEY:
    raise ValueError('GROQ_API_KEY nahi mili! GitHub Secrets ya config file check karein.')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')

# Groq client initialization
_client = Groq(api_key=GROQ_API_KEY)

# ═══════════════════════════════════════════════════════════════════
# ULTRA-VIRAL TOPIC POOL v2.0
# Formula: Forbidden Knowledge + Personal Threat + Instant Payoff
# ═══════════════════════════════════════════════════════════════════
TOPIC_POOL = [

    # ── DARK PSYCHOLOGY: Control & Manipulation ──────────────────
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

    # ── HUMAN BEHAVIOR: Hidden & Shocking ────────────────────────
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

    # ── BRAIN & BODY SCIENCE: Fear, Mystery, Awe ─────────────────
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

    # ── SOCIAL DYNAMICS: Power, Status, Envy ─────────────────────
    "The dark psychological reason successful people are hated by their closest friends",
    "How to instantly detect a fake friend using one simple psychological test",
    "The silent war psychology: what highly secure people never do in arguments",
    "Why people who were humiliated in public become the most dangerous enemies",
    "The psychological reason your enemies smile the widest at your success",
    "What happens to your brain chemistry when someone ignores you on purpose",
    "The dark truth about why genuinely confident people speak less",
    "The psychological reason people sabotage relationships right before they succeed",

    # ── IDENTITY & SELF: Eerie Self-Discovery ─────────────────────
    "The unsettling truth about what your recurring nightmare is actually warning you about",
    "Psychology confirms most people are living a life chosen by someone else entirely",
    "The terrifying documented case where a person woke up speaking a foreign language",
    "What happens to your sense of identity when you go completely silent for 72 hours",
    "Psychologists say the version of you that exists at 3AM is your true self",
    "The dark reason highly empathetic people often become emotionally numb over time",
]

# ═══════════════════════════════════════════════════════════════════
# SYSTEM PROMPT v3.0 — MAXIMUM SCROLL-STOP ENGINEERING
# ═══════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = (
    "You are a world-class short-form video scriptwriter. You specialize in Dark Psychology, "
    "Hidden Brain Science, and Forbidden Human Behavior — engineered for maximum scroll-stop retention "
    "on TikTok, YouTube Shorts, and Instagram Reels. Your audience: curious, skeptical adults aged 18-45 in the USA and UK.\n\n"

    "ABSOLUTE RULES:\n"
    "1. TOTAL WORD COUNT: 110-140 words ONLY. This equals exactly 45-58 seconds of speech. Count strictly.\n"
    "2. VOICE: Always second-person. Use 'you', 'your', 'you've', 'you're' to make it feel personal.\n"
    "3. TONE: Mysterious. Clinical. Dark. Authoritative. Like a forensic psychologist exposing hidden truths.\n"
    "4. NO FILLER: Zero generic openers. Never say 'welcome', 'today we', 'in this video', or 'hey guys'.\n\n"

    "HOOK FORMULA — The first 1-2 sentences are THE ENTIRE GAME:\n"
    "The hook MUST do ONE of these:\n"
    "  A) STATE A FORBIDDEN FACT:  'Psychologists confirmed something about you that no one is allowed to say publicly.'\n"
    "  B) ISSUE A PERSONAL THREAT: 'Someone in your life is using this exact technique on you right now.'\n"
    "  C) TRIGGER IDENTITY SHOCK:  'The person you think you are does not actually exist — here is the proof.'\n"
    "  D) CREATE URGENT CURIOSITY: 'There are 7 seconds left before your brain makes a decision you cannot reverse.'\n"
    "Use POWER WORDS: 'confirmed', 'documented', 'forbidden', 'classified', 'terrifying', 'they never told you'.\n"
    "The hook must feel like a secret the viewer was never supposed to know.\n\n"

    "SCRIPT STRUCTURE:\n"
    "  [HOOK]   — 1-2 sentences. Scroll-stop. Identity shock. Forbidden knowledge.\n"
    "  [REVEAL] — 3-4 sentences. The dark mechanism or psychology explained clinically.\n"
    "  [PROOF]  — 2-3 sentences. A real documented case, study, or chilling example.\n"
    "  [IMPACT] — 1-2 sentences. What this means for the viewer personally right now.\n"
    "  [CTA]    — 1 sentence. Sharp command to follow for more classified dark psychology.\n\n"

    "BROLL KEYWORDS:\n"
    "Provide exactly 4 dark, cinematic, aesthetic search terms for stock footage.\n"
    "Examples: 'extreme close-up human eye pupil dilation', 'dark silhouette empty corridor 4K',\n"
    "'brain scan glowing neural activity', 'hands shadow psychological thriller'.\n\n"

    "SEO PACKAGE:\n"
    "  Title: Under 60 characters. Include a power word and a curiosity gap.\n"
    "  Description: 150-200 words. Dense with searchable psychology and neuroscience keywords.\n"
    "  Hashtags: Exactly 8 hashtags — mix of viral (#Psychology) and niche (#DarkPsychologyFacts).\n\n"

    "OUTPUT FORMAT:\n"
    "Return ONLY a valid JSON object. No markdown. No explanation. No extra text.\n"
    "{\n"
    '  "topic": "string",\n'
    '  "script": "string — 110 to 140 words, opens with a massive scroll-stopping hook",\n'
    '  "broll_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],\n'
    '  "seo": {\n'
    '    "title": "string under 60 characters with power word",\n'
    '    "description": "string 150-200 words packed with psychology keywords",\n'
    '    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6", "#tag7", "#tag8"]\n'
    "  }\n"
    "}"
)

# ═══════════════════════════════════════════════════════════════════
# MODEL CHAIN — Fastest to most reliable fallback
# ═══════════════════════════════════════════════════════════════════
MODEL_CHAIN = [
    'llama-3.3-70b-versatile',   # Primary: Best quality + speed
    'llama-3.1-8b-instant',      # Fallback 1: Ultra-fast
    'gemma2-9b-it'               # Fallback 2: Safety net
]


def _call_groq(topic: str, model: str) -> dict:
    user_message = (
        f'Generate a complete dark psychology short-form video package for this topic:\n\n'
        f'TOPIC: {topic}\n\n'
        f'CRITICAL INSTRUCTIONS:\n'
        f'— The first sentence MUST be a scroll-stopping hook using the forbidden knowledge or identity threat formula.\n'
        f'— Use "you" and "your" throughout. Make the viewer feel personally exposed.\n'
        f'— Script must be 110-140 words. Count carefully.\n'
        f'— Return ONLY the JSON object. No extra text.'
    )
    logger.info(f'Calling Groq model: {model}')
    response = _client.chat.completions.create(
        model=model,
        max_tokens=1500,
        temperature=0.88,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': user_message}
        ]
    )
    raw_text = response.choices[0].message.content.strip()
    logger.info(f'Response received: {len(raw_text)} chars')

    # Strip accidental markdown fences
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
    """
    Main entry point. Pass a topic string or leave None for random selection.
    Returns a validated dict with keys: topic, script, broll_keywords, seo.
    """
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
    """Ensure all required keys exist and types are correct."""
    for key in ('topic', 'script', 'broll_keywords', 'seo'):
        if key not in data:
            data[key] = 'Missing data'

    seo = data.get('seo', {})
    if not isinstance(seo, dict):
        data['seo'] = seo = {}
    for key in ('title', 'description', 'hashtags'):
        if key not in seo:
            seo[key] = 'Missing seo data'

    # broll_keywords must be a list of 4
    if not isinstance(data['broll_keywords'], list):
        data['broll_keywords'] = [
            'dark aesthetic cinematic',
            'mysterious silhouette shadow',
            'brain neural activity glow',
            'eye close-up macro thriller'
        ]
    if len(data['broll_keywords']) < 4:
        defaults = ['dark corridor 4K', 'psychological thriller shadow',
                    'human brain scan', 'closeup eye fear']
        data['broll_keywords'].extend(defaults[:4 - len(data['broll_keywords'])])

    # Title character limit
    if isinstance(seo.get('title'), str) and len(seo['title']) > 100:
        seo['title'] = seo['title'][:95] + '...'

    # Hashtags must be a list of exactly 8
    if not isinstance(seo.get('hashtags'), list):
        seo['hashtags'] = [
            '#DarkPsychology', '#PsychologyFacts', '#MindControl',
            '#HumanBehavior', '#BrainScience', '#MindMysteries',
            '#NeuralPsychology', '#ForbiddenKnowledge'
        ]
    elif len(seo['hashtags']) < 8:
        padding = ['#Psychology', '#Behavior', '#MindHacks', '#BrainFacts']
        seo['hashtags'].extend(padding[:8 - len(seo['hashtags'])])


def _log_quality_check(data: dict) -> None:
    """Quick quality audit of the generated script."""
    script = data.get('script', '')
    word_count = len(script.split())
    has_you = 'you' in script.lower()
    title_len = len(data.get('seo', {}).get('title', ''))

    logger.info(f'  Word count : {word_count} (target: 110-140)')
    logger.info(f'  Uses "you" : {has_you}')
    logger.info(f'  Title len  : {title_len} chars (limit: 60)')

    if word_count < 100:
        logger.warning('  Script may be too short!')
    elif word_count > 150:
        logger.warning('  Script may be too long — check pacing.')
    if not has_you:
        logger.warning('  Script lacks second-person voice — hook may be weak.')


def build_word_timings(script: str, audio_duration: float) -> list[dict]:
    """
    Distribute words evenly across audio_duration.
    Returns list of {word, start, end} dicts for subtitle/caption sync.
    """
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


# ── Quick test run ───────────────────────────────────────────────
if __name__ == '__main__':
    import pprint
    print('\n' + '=' * 60)
    print('  DARK PSYCHOLOGY VIDEO SCRIPT GENERATOR')
    print('  AI Dark Realities · Short-Form Pipeline v2.0')
    print('=' * 60 + '\n')
    result = generate_script()
    pprint.pprint(result, width=80)
    print('\n' + '=' * 60)
    print(f'  Done | Word count: {len(result.get("script", "").split())}')
    print('=' * 60)
