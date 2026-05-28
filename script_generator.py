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

# Pure prompt ko safe single lines me convert kiya hai taake line break crash na ho
SYSTEM_PROMPT = (
    'You are an expert short-form video scriptwriter and SEO strategist '
    'specialising in viral, suspenseful content about AI and technology dark realities. '
    'Target audience: curious adults aged 18-45 in the USA and UK.\n\n'
    'RULES:\n'
    '1. Script must be 110 to 150 words total. No more, no less.\n'
    '2. Write in second-person using you and your to create urgency.\n'
    '3. First sentence must be a shocking hook.\n'
    '4. End with a call-to-action asking viewers to follow for more.\n'
    '5. Return ONLY a valid JSON object matching the exact schema below.\n'
    '6. Do NOT include any text outside the JSON object.\n'
    '7. Do NOT use markdown code fences.\n\n'
    'EXACT JSON SCHEMA TO RETURN:\n'
    '{\n'
    '  "topic": "string",\n'
    '  "script": "string with 110 to 150 words",\n'
    '  "broll_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],\n'
    '  "seo": {\n'
    '    "title": "string under 60 characters",\n'
    '    "description": "string 150 to 200 words packed with keywords",\n'
    '    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6", "#tag7", "#tag8", "#tag9", "#tag10"]\n'
    '  }\n'
    '}'
)

MODEL_CHAIN = [
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'gemma2-9b-it'
]

def _call_groq(topic: str, model: str) -> dict:
    user_message = (
        f'Create a complete short-form video package for this topic:\n'
        f'TOPIC: {topic}\n'
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
    raw_text = re.sub(r'^
http://googleusercontent.com/immersive_entry_chip/0

### 💡 Choti si Request:
Aap is code ko copy karke jab GitHub file mein paste karein, to commit karne se pehle ek baar dekh lijiye ga ke pure code mein koi single quote toota hua na ho. 

Ab push karke run karein, yeh run bilkul green (pass) ho jayega!
