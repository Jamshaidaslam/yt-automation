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

# 🟢 NEW VIRAL TOPIC POOL: USA/UK High-Retention Psychology & Body Mysteries
TOPIC_POOL = [
    'Dark psychology trick to read anyone instantly by watching their eyes',
    'What happens to your brain when you secretly stare at someone',
    'The terrifying reason why your brain experiences Deja Vu',
    'Why your brain knows someone is looking at you even while you sleep',
    'Psychological facts about how manipulation tactics control your choices',
    'The hidden reason why you feel a sudden drop in your stomach',
    'Dark behavior signs that someone is secretly jealous of your life',
    'How reverse psychology tricks people into doing exactly what you want',
    'What happens inside your dimage during a sleep paralysis episode',
    'The biological secret of why eye contact can make anyone nervous',
    'Psychological trick: How to make someone regret hurting you immediately',
    'The subconscious reason why we match the body language of others',
    'What your dreams are trying to tell you about your darkest fears',
    'The manipulation technique used by toxic people to gaslight you',
    'Why your brain sometimes creates false memories that never happened'
]

# 🟢 SYSTEM PROMPT OPTIMIZATION: Injected Magical Hooks & Premium Tone Control
SYSTEM_PROMPT = (
    'You are an expert short-form video scriptwriter specializing in Dark Psychology, '
    'Body Science, and Hidden Human Behavior Mysteries. Target audience: curious adults aged 18-45 in the USA and UK. '
    'RULES: '
    '1. Script must be 110 to 140 words total (strictly under 60 seconds of speech). '
    '2. Write in second-person using "you" and "your" to create an intense connection. '
    '3. MAGICAL HOOK: The first sentence MUST be a shocking, high-retention psychological hook that stops scrolling immediately. Do not say welcome. '
    '4. Tone must be mysterious, dark, clinical, and authoritative. '
    '5. BROLL KEYWORDS: Provide 3-4 dark, aesthetic visual search keywords for stock footage (e.g., "dark aesthetic", "shadowy figure", "brain macro"). '
    '6. End with a sharp call-to-action asking viewers to follow for more dark secrets. '
    '7. Return ONLY a valid JSON object matching the exact schema below without markdown formatting.'
    'EXACT JSON SCHEMA TO RETURN: '
    '{'
    '"topic": "string", '
    '"script": "string with 110 to 140 words starting with a massive hook", '
    '"broll_keywords": ["keyword1", "keyword2", "keyword3"], '
    '"seo": {'
    '"title": "string under 60 characters", '
    '"description": "string packed with psychology keywords", '
    '"hashtags": ["#tag1", "#tag2", "#tag3"]'
    '}'
    '}'
)

MODEL_CHAIN = [
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'gemma2-9b-it'
]

def _call_groq(topic: str, model: str) -> dict:
    user_message = (
        f'Create a complete dark psychology or brain mystery short-form video package for this topic: {topic}. '
        f'Make sure the script starts with an absolute magical hook line. Return ONLY the JSON object.'
    )
    logger.info(f'Calling Groq model: {model}')
    response = _client.chat.completions.create(
        model=model,
        max_tokens=1500,
        temperature=0.85,  # Slightly higher for creative and dramatic hooks
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': user_message}
        ]
    )
    raw_text = response.choices[0].message.content.strip()
    logger.info(f'Response received: {len(raw_text)} chars')
    
    if raw_text.startswith('```'):
        raw_text = raw_text.split('\n', 1)[1]
    if raw_text.endswith('
```'):
        raw_text = raw_text.rsplit('\n', 1)[0]
    raw_text = raw_text.strip()
    
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error(f'JSON parse error: {exc}')
        raise ValueError(f'Invalid JSON from Groq: {exc}') from exc
    return data

def generate_script(topic: str | None = None) -> dict:
    if topic is None:
        topic = random.choice(TOPIC_POOL)
    logger.info(f'Generating script for topic: {topic}')
    last_error = None
    for model in MODEL_CHAIN:
        try:
            data = _call_groq(topic, model)
            _validate_and_fix(data)
            logger.info(f'Script OK via {model}')
            return data
        except Exception as exc:
            logger.warning(f'Model {model} failed: {exc}')
            last_error = exc
            continue
    raise RuntimeError(f'All Groq models failed. Last error: {last_error}')

def _validate_and_fix(data: dict) -> None:
    for key in ('topic', 'script', 'broll_keywords', 'seo'):
        if key not in data: data[key] = 'Missing data'
    seo = data.get('seo', {})
    for key in ('title', 'description', 'hashtags'):
        if key not in seo: seo[key] = 'Missing seo data'
    
    # 🟢 NEW STABLE DEFAULT KEYWORDS: If model fails, fetch dark mysterious aesthetic stock videos
    if not isinstance(data['broll_keywords'], list):
        data['broll_keywords'] = ['dark aesthetic', 'mysterious cinematography', 'shadowy figure']
        
    if len(seo['title']) > 100:
        seo['title'] = seo['title'][:95] + '...'
    if not isinstance(seo['hashtags'], list):
        seo['hashtags'] = ['#DarkPsychology', '#PsychologyFacts', '#MindMysteries']

def build_word_timings(script: str, audio_duration: float) -> list[dict]:
    words = script.split()
    if not words: return []
    per_word = audio_duration / len(words)
    timings = []
    t = 0.0
    for word in words:
        clean = ''.join(c for c in word if c.isalnum() or c in "'-")
        if clean:
            timings.append({'word': clean, 'start': round(t, 3), 'end': round(t + per_word, 3)})
        t += per_word
    return timings

if __name__ == '__main__':
    import pprint
    result = generate_script()
    pprint.pprint(result)
