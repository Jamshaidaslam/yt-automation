"""
script_generator.py — Ultimate Viral Dark Psychology Engine
AI Dark Realities · USA/UK Viral Shorts Generator
"""

import json
import os
import re
import logging
from groq import Groq

logger = logging.getLogger(**name**)

def generate_script(topic: str) -> dict:
logger.info(f"🧠 Generating viral dark psychology script for topic: [{topic}]")

```
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Missing GROQ_API_KEY environment variable.")

client = Groq(api_key=api_key)

prompt_lines = [
    "You are a world-class viral content architect specializing in Dark Psychology, Human Behavior, Hidden Truths, Manipulation Tactics, Cognitive Biases, Forbidden Knowledge, and Mystery-based short-form videos for USA, UK, Canada, and Australia audiences.",

    "Your mission is to create highly addictive YouTube Shorts, TikTok, Instagram Reels, and Facebook Reels scripts engineered for maximum audience retention, curiosity, watch time, shares, comments, and replays.",

    "CONTENT STYLE:",
    "- Extremely cinematic and emotionally intense.",
    "- Dark, mysterious, psychologically powerful, and intellectually stimulating.",
    "- Every sentence must increase curiosity.",
    "- Sound like a hidden secret.",
    "- Create an irresistible need to hear the ending.",

    "HOOK REQUIREMENTS:",
    "- First sentence must instantly stop scrolling.",
    "- Start with a shocking fact, disturbing question, hidden truth, or counterintuitive statement.",
    "- Create tension in the first 3 seconds.",
    "- Avoid generic introductions.",

    "RETENTION REQUIREMENTS:",
    "- Every scene must reveal new information.",
    "- No filler content.",
    "- Escalate suspense continuously.",
    "- Build curiosity loops.",
    "- Every sentence must naturally pull viewers to the next sentence.",

    "VOICEOVER REQUIREMENTS:",
    "- MUST contain between 90 and 130 words.",
    "- MUST be one continuous paragraph.",
    "- Duration target: 35-55 seconds.",
    "- Structure: Hook → Explanation → Revelation → Twist → Conclusion.",
    "- End with a loop sentence that connects back to the opening line.",

    "SCENE REQUIREMENTS:",
    "- Generate EXACTLY 5 scenes.",
    "- Scenes must be chronological.",
    "- Each scene should visually match its voiceover section.",
    "- Each scene must increase mystery and intensity.",

    "VISUAL QUERY REQUIREMENTS:",
    "- Each scene must contain Pexels-friendly search keywords.",
    "- Use keyword phrases only.",
    "- No full sentences.",
    "- Focus on psychology, mystery, shadows, loneliness, fear, manipulation, technology, surveillance, power, secrets, and human emotions.",

    "STRICT OUTPUT FORMAT:",
    "- Return ONLY valid JSON.",
    "- No markdown.",
    "- No explanations.",
    "- No text outside JSON.",

    "JSON STRUCTURE:",

    "{",
    '  "title": "High CTR viral title",',
    '  "hook": "Scroll stopping opening line",',
    '  "voiceover": "90-130 word narration",',
    '  "scenes": [',
    '    {',
    '      "scene_number": 1,',
    '      "visual_query": "dark silhouette portrait, mystery shadow face"',
    '    },',
    '    {',
    '      "scene_number": 2,',
    '      "visual_query": "moody person alone, cinematic darkness"',
    '    },',
    '    {',
    '      "scene_number": 3,',
    '      "visual_query": "phone glow face, surveillance concept"',
    '    },',
    '    {',
    '      "scene_number": 4,',
    '      "visual_query": "human eye closeup, psychological tension"',
    '    },',
    '    {',
    '      "scene_number": 5,',
    '      "visual_query": "mysterious silhouette walking, dark realization"',
    '    }',
    '  ],',
    '  "psychological_takeaway": "Powerful lesson",',
    '  "engagement_question": "Comment generating question"',
    "}"
]

system_prompt = "\n".join(prompt_lines)

user_prompt = f"""
```

Create a highly viral dark psychology short-form video script.

TOPIC:
{topic if topic else "Dark Psychology"}

Requirements:

* Voiceover must contain 90 to 130 words.
* Exactly 5 scenes.
* Cinematic storytelling.
* Strong curiosity gap.
* Hidden psychological insight.
* Unexpected twist.
* Viral ending.
* USA/UK audience style.
* End with a sentence that naturally loops back to the first sentence.

Return only valid JSON.
"""

```
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0.85,
    max_tokens=1200,
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
)

raw_output = response.choices[0].message.content.strip()

try:
    data = json.loads(raw_output)

except json.JSONDecodeError:

    logger.warning("⚠️ Invalid JSON returned. Attempting extraction...")

    match = re.search(r'\{.*\}', raw_output, re.DOTALL)

    if not match:
        raise RuntimeError(
            f"Could not parse JSON from model output:\n{raw_output}"
        )

    data = json.loads(match.group(0))

voiceover = data.get("voiceover", "")

word_count = len(voiceover.split())

logger.info(
    f"✅ Script generated successfully | Words: {word_count}"
)

if word_count < 90:
    logger.warning(
        f"⚠️ Voiceover too short ({word_count} words). Consider regenerating."
    )

if word_count > 130:
    logger.warning(
        f"⚠️ Voiceover too long ({word_count} words). Consider regenerating."
    )

return data
```

"""
