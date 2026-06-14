import json
import os
import logging
import random
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOPIC_POOL = [
    "Why you wake up at 3AM",
    "Why you feel like falling while sleeping",
    "Why your brain creates false memories",
    "Why you get déjà vu",
    "The science of nightmares",
    "Why people fear the dark",
    "How your brain learns while you sleep",
    "Why you suddenly forget names",
    "The psychology of first impressions",
    "Why people fall for toxic relationships"
]

HOOKS = [
    "This happens to you every day and you never notice it.",
    "Your brain is hiding something from you.",
    "Almost nobody knows why this happens.",
    "If this happens to you, pay attention.",
    "You are doing this without realizing it.",
    "Scientists were shocked when they discovered this."
]

CTAS = [
    "Save this before you forget it.",
    "Follow for more mind-blowing facts.",
    "Share this with someone who needs to know.",
    "Most people never learn this.",
    "You will notice this tonight."
]


def generate_script(topic: str):

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found.")

    client = Groq(api_key=api_key)

    hook = random.choice(HOOKS)
    cta = random.choice(CTAS)

    prompt = f"""
You are an expert viral YouTube Shorts writer.

Create a SHORTS script that maximizes audience retention.

RULES:

1. First sentence must create curiosity.
2. Use simple human language.
3. Create suspense and open loops.
4. Add a surprising twist near the end.
5. Keep viewers watching until the final sentence.
6. No robotic writing.
7. Sentences must be short.
8. Tone: mysterious and exciting.

TOPIC:
{topic}

Return ONLY valid JSON.

{{
    "title":"",
    "description":"",
    "tags":"",
    "voiceover":"",
    "hook":"{hook}",
    "cta":"{cta}",
    "retention_score":"",
    "scenes":[
        {{
            "time":"0-3",
            "visual_query":""
        }},
        {{
            "time":"3-6",
            "visual_query":""
        }},
        {{
            "time":"6-10",
            "visual_query":""
        }},
        {{
            "time":"10-15",
            "visual_query":""
        }},
        {{
            "time":"15-20",
            "visual_query":""
        }},
        {{
            "time":"20-30",
            "visual_query":""
        }}
    ],
    "thumbnail_line1":"",
    "thumbnail_line2":""
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1200,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        if not content.startswith("{"):
            content = content[content.find("{"):]

        return json.loads(content)

    except Exception as e:
        logger.error(e)
        return {
            "error": str(e)
        }


def pick_topic_for_run():
    return random.choice(TOPIC_POOL)


if __name__ == "__main__":

    topic = pick_topic_for_run()

    print(f"Generating script for: {topic}")

    result = generate_script(topic)

    print(json.dumps(result, indent=4, ensure_ascii=False))
