"""
script_generator.py — Groq Script & SEO Generation
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────────
"""

import json
import re
import random
import logging
import sys
import os

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

TOPIC_POOL = [
    'How AI surveillance cameras track your face without consent',
    'The hidden algorithm that decided you did not get that job',
    'Why ChatGPT sometimes lies with complete confidence',
    'The dark side of AI-generated deepfake voices scamming families',
    'How social media AI is engineered to trigger dopamine addiction',
    'The secret score banks use to predict your financial future',
    'AI that predicts crime before it happens and gets it wrong',
    'How recommendation algorithms trap you in an echo chamber forever',
    'The company that sells your location data to anyone who pays',
    'Why AI systems trained on biased data make racist decisions',
    'The ghost workers behind every AI model you have ever used',
    'How Google AI knows your search intent before you finish typing',
    'The AI emotion-detection system used in job interviews',
    'Why AI writing detectors are dangerously inaccurate',
    'The military drones that choose their own targets using AI',
    'How TikTok algorithm knows your secrets better than your therapist',
    'The psychological manipulation tactics built into every app you use',
    'AI-generated propaganda and how fake news is now indistinguishable',
    'The dark truth about how AI models are trained on stolen art',
    'Why AI hallucinations could get someone killed in a hospital'
]

# Crash se bachne k liye bilkul plain single line pieces ko joda hai
SYSTEM_PROMPT = (
    'You are an expert short-form video scriptwriter and SEO strategist. '
    'Target audience: curious adults aged 18-45 in the USA and UK. '
    'RULES: '
    '1. Script must be 110 to 150 words total. '
    '2. Write in second-person using you and your. '
    '3. First sentence must be a shocking hook. '
    '4. End with a call-to-action asking viewers to follow for more. '
    '5. Return ONLY a valid JSON object matching the exact schema below. '
    '6. Do NOT include any markdown code fences. '
    'EXACT JSON SCHEMA TO RETURN: '
    '{'
    '"topic": "string", '
    '"script": "string with 110 to 150 words", '
    '"broll_keywords": ["keyword1", "keyword2", "keyword3"], '
    '"seo": {'
    '"title": "string under 60 characters", '
    '"description": "string packed with keywords", '
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
        f'Create a complete short-form video package for this topic: {topic}. '
        f'Return ONLY the JSON object. No extra text. No markdown.'
    )
    logger.info(f'Calling Groq model: {model}')
    response = _client.chat.completions.create(
        model=model,
        max_tokens=1500,
        temperature=0.8,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': user_message}
        ]
    )
    raw_text = response.choices[0].message.content.strip()
    logger.info(f'Response received: {len(raw_text)} chars')
    
    # Bilkul safe cleaning without complex regex patterns
    if raw_text.startswith('```'):
        raw_text = raw_text.split('\n', 1)[1]
    if raw_text.endswith('```'):
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
    if not isinstance(data['broll_keywords'], list):
        data['broll_keywords'] = ['artificial intelligence technology', 'data privacy surveillance']
    if len(seo['title']) > 100:
        seo['title'] = seo['title'][:95] + '...'
    if not isinstance(seo['hashtags'], list):
        seo['hashtags'] = ['#AIFacts', '#DarkReality', '#Shorts']

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
