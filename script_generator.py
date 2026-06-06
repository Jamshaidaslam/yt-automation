import json
import os
import logging
import random
from groq import Groq

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════
# 120 VIRAL TOPIC POOL
# ═══════════════
TOPIC_POOL = [
    {"topic": "Why YOU feel like falling while sleeping", "cta": "Save this — why YOUR brain does this", "scenes_theme": "falling in dream, sleeping, sudden jerk"},
    {"topic": "How YOUR brain works while YOU sleep", "cta": "Follow — discover YOUR hidden brain power", "scenes_theme": "glowing brain animation, REM sleep"},
    {"topic": "Why YOU experience deja vu", "cta": "Save this — is YOUR reality a glitch", "scenes_theme": "mirror reflection, glitch effect"},
    {"topic": "The science behind YOUR vivid nightmares", "cta": "Follow — conquer YOUR fear today", "scenes_theme": "dark dreams, shadows, racing heartbeat"},
    {"topic": "Why YOU talk in YOUR sleep", "cta": "Save this — secrets YOU tell yourself", "scenes_theme": "sleeping person, dark room, whispers"},
    {"topic": "Can YOU train YOUR brain to lucid dream", "cta": "Follow — take control of YOUR dreams", "scenes_theme": "astral projection, sleepy eyes"},
    {"topic": "What happens to YOUR brain when YOU die", "cta": "Save this — dark mystery revealed", "scenes_theme": "bright light, brain scan fading"},
    {"topic": "Why YOU forget YOUR dreams instantly", "cta": "Follow — keep YOUR dream memories", "scenes_theme": "fading mist, waking up, writing in journal"},
    {"topic": "How YOUR brain creates imaginary people", "cta": "Save this — why YOU see faces", "scenes_theme": "crowded street, blurred faces"},
    {"topic": "Why YOU wake up at 3AM", "cta": "Follow — discover YOUR body clock", "scenes_theme": "clock ticking 3AM, dark room"},
    {"topic": "The truth about YOUR subconscious mind", "cta": "Save this — unlock YOUR hidden potential", "scenes_theme": "iceberg model, deep ocean"},
    {"topic": "Why YOU have intrusive thoughts", "cta": "Follow — control YOUR inner voice", "scenes_theme": "cluttered mind, racing thoughts"},
    {"topic": "How YOUR brain handles heartbreak", "cta": "Save this — heal YOUR broken self", "scenes_theme": "heart breaking animation, rain"},
    {"topic": "Why YOU feel someone watching YOU", "cta": "Follow — trust YOUR survival instinct", "scenes_theme": "looking behind, empty corridor"},
    {"topic": "The mystery of YOUR false memories", "cta": "Save this — can YOU trust YOUR mind", "scenes_theme": "old photo, distorted memory"},
    {"topic": "Why YOU get brain freezes", "cta": "Follow — stop YOUR pain now", "scenes_theme": "ice cream, frozen reaction"},
    {"topic": "How YOUR brain learns while YOU nap", "cta": "Save this — boost YOUR intelligence", "scenes_theme": "sleeping with books, brain glowing"},
    {"topic": "Why YOU crave sugar at night", "cta": "Follow — fix YOUR sleep hunger", "scenes_theme": "late night fridge, snacks"},
    {"topic": "The secret to YOUR extreme focus", "cta": "Save this — hack YOUR flow state", "scenes_theme": "focused eye, clock speed"},
    {"topic": "Why YOU struggle to wake up", "cta": "Follow — beat YOUR morning fatigue", "scenes_theme": "alarm clock, heavy eyelids"},
    {"topic": "How YOUR brain maps YOUR house", "cta": "Save this — navigate in dark", "scenes_theme": "dark hallway, walking blindly"},
    {"topic": "Why YOU feel small in big places", "cta": "Follow — understand YOUR perspective", "scenes_theme": "skyscrapers, looking up"},
    {"topic": "The reason YOU fear the dark", "cta": "Save this — face YOUR primal fear", "scenes_theme": "shadows, flickering light"},
    {"topic": "How YOUR brain filters out noise", "cta": "Follow — hear what YOU need", "scenes_theme": "busy street, silence effect"},
    {"topic": "Why YOU talk to YOURSELF", "cta": "Save this — it makes YOU smarter", "scenes_theme": "mirror talking, internal monologue"},
    {"topic": "How YOU can boost YOUR memory", "cta": "Follow — never forget a face", "scenes_theme": "mind palace, file cabinet"},
    {"topic": "The science of YOUR sudden anger", "cta": "Save this — control YOUR emotions", "scenes_theme": "burning fire, red filter"},
    {"topic": "Why YOU procrastinate on YOUR goals", "cta": "Follow — destroy YOUR laziness", "scenes_theme": "clock ticking, unfinished work"},
    {"topic": "How YOUR brain sees beauty", "cta": "Save this — define YOUR taste", "scenes_theme": "art gallery, golden ratio"},
    {"topic": "Why YOU feel connected to strangers", "cta": "Follow — discover YOUR soul link", "scenes_theme": "eye contact, crowd moving"},
    {"topic": "How far can the human eye actually see", "cta": "Save this — test YOUR vision limits", "scenes_theme": "horizon, stars, telescope"},
    {"topic": "Why YOU blink and what it hides", "cta": "Follow — see what YOU are missing", "scenes_theme": "blinking eye, slow motion"},
    {"topic": "The colors YOU cannot see", "cta": "Save this — expand YOUR vision", "scenes_theme": "spectrum, blurred vision"},
    {"topic": "Why YOUR eyes lie to YOU", "cta": "Follow — optical illusion secrets", "scenes_theme": "optical illusions, swirl"},
    {"topic": "How YOUR eyes record YOUR memories", "cta": "Save this — unlock YOUR visual memory", "scenes_theme": "iris, camera lens"},
    {"topic": "The reason YOU see spots in light", "cta": "Follow — understand YOUR vision", "scenes_theme": "bright sky, floating spots"},
    {"topic": "Why YOU cry when YOU are happy", "cta": "Save this — emotional release", "scenes_theme": "happy tears, smiling face"},
    {"topic": "How YOUR eyes change with YOUR mood", "cta": "Follow — read THEIR eye changes", "scenes_theme": "pupil dilation, anger gaze"},
    {"topic": "Why YOU need glasses for YOUR sight", "cta": "Save this — frame YOUR intelligence", "scenes_theme": "glasses, vision chart"},
    {"topic": "Can YOU see in total darkness", "cta": "Follow — hack YOUR night vision", "scenes_theme": "night mode, dark room"},
    {"topic": "Why YOU prefer YOUR left or right eye", "cta": "Save this — test YOUR dominance", "scenes_theme": "eye testing, focus"},
    {"topic": "The mystery of YOUR peripheral vision", "cta": "Follow — sense what IS behind YOU", "scenes_theme": "shadow in corner, turning head"},
    {"topic": "Why YOUR eyes get tired at night", "cta": "Save this — refresh YOUR sight", "scenes_theme": "rubbing eyes, screen light"},
    {"topic": "How YOU can improve YOUR vision", "cta": "Follow — see clearly forever", "scenes_theme": "green scenery, exercise"},
    {"topic": "Why YOU hate bright lights", "cta": "Save this — protect YOUR eyes", "scenes_theme": "sunlight, squinting"},
    {"topic": "The truth about YOUR eye color", "cta": "Follow — why YOU are unique", "scenes_theme": "extreme close up eyes"},
    {"topic": "Why YOU see light trails at night", "cta": "Save this — YOUR brain glitch", "scenes_theme": "car lights, motion blur"},
    {"topic": "How YOUR eyes stay hydrated", "cta": "Follow — secret of YOUR tears", "scenes_theme": "eye drops, moisture"},
    {"topic": "Why YOU look away when lying", "cta": "Save this — catch THEM lying", "scenes_theme": "shifty eyes, looking away"},
    {"topic": "The speed of YOUR visual processing", "cta": "Follow — YOU are faster than light", "scenes_theme": "fast cuts, data stream"},
    {"topic": "Why YOU see ghosts in the corner", "cta": "Save this — brain trick explained", "scenes_theme": "dark corner, ghost figure"},
    {"topic": "How YOUR eyes show YOUR age", "cta": "Follow — keep YOUR eyes young", "scenes_theme": "fine lines, mirror gaze"},
    {"topic": "Why YOU find symmetry attractive", "cta": "Save this — biology of beauty", "scenes_theme": "perfect face, grid"},
    {"topic": "The secret behind YOUR eye twitch", "cta": "Follow — stop YOUR stress now", "scenes_theme": "twitching eye, stress"},
    {"topic": "How YOUR eyes help YOU balance", "cta": "Save this — walk with poise", "scenes_theme": "balancing, tightrope"},
    {"topic": "Why YOU blink less when focusing", "cta": "Follow — master YOUR attention", "scenes_theme": "deep focus, reading"},
    {"topic": "The connection between eyes and mind", "cta": "Save this — see THEIR thoughts", "scenes_theme": "mind map, eye contact"},
    {"topic": "Why YOU squint to see clearly", "cta": "Follow — understand YOUR vision", "scenes_theme": "squinting, blur"},
    {"topic": "How YOUR eyes interpret 3D depth", "cta": "Save this — see YOUR world", "scenes_theme": "depth perception, 3D"},
    {"topic": "Why YOU love watching sunsets", "cta": "Follow — colors YOU adore", "scenes_theme": "sunset, silhouette"},
    {"topic": "How YOU can read anyone’s mind", "cta": "Save this — master YOUR observation", "scenes_theme": "staring, thinking, mental bridge"},
    {"topic": "The hidden language of YOUR eyes", "cta": "Follow — reveal THEIR inner thoughts", "scenes_theme": "eye contact, pupil scan"},
    {"topic": "How to detect a lie in seconds", "cta": "Save this — never be fooled again", "scenes_theme": "liar face, fake smile"},
    {"topic": "The power of silence in conversation", "cta": "Follow — command YOUR room today", "scenes_theme": "silence, power, influence"},
    {"topic": "How YOU can influence their decisions", "cta": "Save this — master YOUR persuasion", "scenes_theme": "nodding, handshake"},
    {"topic": "Why YOU feel attracted to THEM", "cta": "Follow — science of YOUR crush", "scenes_theme": "romantic lights, heart beat"},
    {"topic": "The secret sign of YOUR confidence", "cta": "Save this — walk like a king", "scenes_theme": "confident walk, posture"},
    {"topic": "How to make anyone trust YOU", "cta": "Follow — gain THEIR total loyalty", "scenes_theme": "trusting smile, eye lock"},
    {"topic": "Why YOU get manipulated easily", "cta": "Save this — break YOUR cycle", "scenes_theme": "strings attached, puppet"},
    {"topic": "The art of reading body language", "cta": "Follow — know THEIR next move", "scenes_theme": "body stance, gestures"},
    {"topic": "How to win every single argument", "cta": "Save this — stay calm and win", "scenes_theme": "arguing, winning look"},
    {"topic": "Why YOU struggle with eye contact", "cta": "Follow — fix YOUR social anxiety", "scenes_theme": "avoiding gaze, nervous"},
    {"topic": "How to spot a fake friend", "cta": "Save this — protect YOUR circle", "scenes_theme": "fake hug, backstab"},
    {"topic": "The science of YOUR first impression", "cta": "Follow — make THEM love YOU", "scenes_theme": "first meeting, handshake"},
    {"topic": "How to hide YOUR emotions", "cta": "Save this — keep YOUR secret", "scenes_theme": "poker face, mask"},
    {"topic": "Why YOU fear rejection so much", "cta": "Follow — kill YOUR fear today", "scenes_theme": "rejection, alone"},
    {"topic": "The trick to command respect", "cta": "Save this — everyone watches YOU", "scenes_theme": "high status, leader"},
    {"topic": "How to read Their hand gestures", "cta": "Follow — see what THEY hide", "scenes_theme": "hands, nervous fidgeting"},
    {"topic": "Why YOU fall for toxic people", "cta": "Save this — break YOUR chains", "scenes_theme": "toxic pattern, warning"},
    {"topic": "How to be the smartest in room", "cta": "Follow — outsmart them all", "scenes_theme": "smart glasses, focus"},
    {"topic": "The secret of YOUR charisma", "cta": "Save this — shine brighter", "scenes_theme": "crowd watching, spotlight"},
    {"topic": "How to detect a fake smile", "cta": "Follow — see THEIR true intent", "scenes_theme": "real smile, fake smile"},
    {"topic": "Why YOU apologize too much", "cta": "Save this — stop being weak", "scenes_theme": "apologizing, bowing"},
    {"topic": "How to keep YOUR mystery alive", "cta": "Follow — they will crave YOU", "scenes_theme": "shadowy figure, enigma"},
    {"topic": "The psychological trigger of love", "cta": "Save this — trigger THEIR heart", "scenes_theme": "love notes, heartbeat"},
    {"topic": "How to read Their foot position", "cta": "Follow — know if THEY want out", "scenes_theme": "feet pointed away, walking"},
    {"topic": "Why YOU need solitude to grow", "cta": "Save this — power of being alone", "scenes_theme": "meditating, mountain top"},
    {"topic": "How to handle a bully silently", "cta": "Follow — crush THEM with calm", "scenes_theme": "calm face, staring down"},
    {"topic": "The science of YOUR intuition", "cta": "Save this — trust YOUR gut", "scenes_theme": "inner light, decision"},
    {"topic": "Why YOU crave validation from them", "cta": "Follow — be enough for YOURSELF", "scenes_theme": "mirror, self-worth"},
    {"topic": "What YOUR body language says about YOU", "cta": "Follow — fix YOUR posture today", "scenes_theme": "posture, confident stance"},
    {"topic": "The sub-conscious signs someone likes YOU", "cta": "Save this — know their true feelings", "scenes_theme": "flirting, shy looks"},
    {"topic": "How to spot a fake person instantly", "cta": "Follow — protect YOUR energy", "scenes_theme": "fake smile, walk away"},
    {"topic": "Why YOU should never cross YOUR arms", "cta": "Save this — look more open to THEM", "scenes_theme": "crossed arms, open"},
    {"topic": "The secret signal of YOUR feet direction", "cta": "Follow — read THEIR true intentions", "scenes_theme": "feet, walking away"},
    {"topic": "How to dominate with YOUR walk", "cta": "Save this — own the pavement", "scenes_theme": "confident walk, street"},
    {"topic": "Why YOU touch YOUR face when lying", "cta": "Follow — catch THEM in the act", "scenes_theme": "touching nose, mouth"},
    {"topic": "The power of leaning towards THEM", "cta": "Save this — show YOUR interest", "scenes_theme": "leaning in, talking"},
    {"topic": "How to sit to look powerful", "cta": "Follow — command THEIR attention", "scenes_theme": "powerful sitting, desk"},
    {"topic": "Why YOU mirror Their movements", "cta": "Save this — you are bonding", "scenes_theme": "mirroring, connection"},
    {"topic": "The sign that THEY are nervous", "cta": "Follow — see THEIR weakness", "scenes_theme": "fidgeting, sweating"},
    {"topic": "How to shake hands like a pro", "cta": "Save this — rule the meeting", "scenes_theme": "firm handshake, eyes"},
    {"topic": "Why YOU look down when shy", "cta": "Follow — hold YOUR head high", "scenes_theme": "looking down, looking up"},
    {"topic": "The meaning of YOUR deep sigh", "cta": "Save this — what YOU really feel", "scenes_theme": "sighing, exhausted"},
    {"topic": "How to use YOUR hands to speak", "cta": "Follow — be more persuasive", "scenes_theme": "hand gestures, focus"},
    {"topic": "Why YOU bite YOUR lip", "cta": "Save this — what it tells THEM", "scenes_theme": "biting lip, temptation"},
    {"topic": "The mystery of YOUR shrug", "cta": "Follow — what YOU really know", "scenes_theme": "shrugging, shoulders"},
    {"topic": "How to stand to look taller", "cta": "Save this — dominate the room", "scenes_theme": "standing tall, posture"},
    {"topic": "Why YOU fidget with YOUR hair", "cta": "Follow — is it nerves or flirting", "scenes_theme": "hair twirling, shy"},
    {"topic": "The truth about YOUR smile", "cta": "Save this — is it real or fake", "scenes_theme": "smile, eye wrinkles"},
    {"topic": "How to tell if THEY are angry", "cta": "Follow — read THEIR jaw tension", "scenes_theme": "clenched jaw, anger"},
    {"topic": "Why YOU point at people", "cta": "Save this — why it is rude", "scenes_theme": "pointing finger, aggressive"},
    {"topic": "The body language of a winner", "cta": "Follow — adopt THIS stance now", "scenes_theme": "victory pose, winning"},
    {"topic": "How to hide YOUR nervousness", "cta": "Save this — stay cool always", "scenes_theme": "deep breath, calm"},
    {"topic": "Why YOU stretch when tired", "cta": "Follow — release YOUR tension", "scenes_theme": "stretching, waking up"},
    {"topic": "The secret of YOUR blink rate", "cta": "Save this — read THEIR anxiety", "scenes_theme": "fast blink, stress"},
    {"topic": "How to use YOUR voice to influence", "cta": "Follow — sound more powerful", "scenes_theme": "microphone, deep voice"},
    {"topic": "Why YOU lean back in chairs", "cta": "Save this — you feel safe", "scenes_theme": "relaxing, chair"},
    {"topic": "The body language of love", "cta": "Follow — see how THEY love YOU", "scenes_theme": "holding hands, closeness"},
    {"topic": "Why YOU turn away from Them", "cta": "Save this — you want distance", "scenes_theme": "turning back, cold"}
]

# ═══════════════
# AI SCRIPT GENERATION LOGIC
# ═══════════════

def generate_script(topic: str):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Error: GROQ_API_KEY environment variable is not set.")
        
    client = Groq(api_key=api_key)

    matched_meta = next((item for item in TOPIC_POOL if item["topic"] == topic), {})
    pool_cta = matched_meta.get("cta", "Save this — you'll use it tomorrow")
    pool_theme = matched_meta.get("scenes_theme", "dark psychology eyes")

    prompt = f"""
    ROLE: Viral Content Expert. Generate a strict JSON object for a 4K viral TikTok/Shorts script.
    
    CONSTRAINTS:
    1. Zero-Frame Hook: Start instantly with YOU/YOUR + VERB + YOU. 
       EXAMPLE: "YOUR BODY IS FALLING RIGHT NOW." (Start with action, no questions).
    2. YOU Density Lock: Every 4th word MUST be YOU/YOUR/YOURS.
    3. Ban Words: The, A, An, Secret, Hack, Trick, Method.
    4. Mandatory CTA: {pool_cta}
    5. Output: Raw JSON ONLY (no markdown, no backticks).

    TOPIC: {topic}
    
    JSON STRUCTURE:
    {{
        "title": "4-5 words MAX. Use YOU/YOUR. No forbidden words.",
        "description": "100-120 words. Viral hook, insight, call to action, 5 hashtags.",
        "tags": "15 comma-separated viral tags.",
        "voiceover": "Fast-paced, dark rhythm. YOU density locked. Start with YOU punch. End with {pool_cta}",
        "scenes": [
            {{"visual_query": "{pool_theme}, macro close up, staring at YOU"}},
            {{"visual_query": "{pool_theme}, pupil dilation macro"}},
            {{"visual_query": "mirror reflection of eyes looking at YOU"}},
            {{"visual_query": "phone camera POV eyes looking at viewer"}}
        ],
        "thumbnail_line1": "2 words MAX. YOU + POWER WORD.",
        "thumbnail_line2": "2 words MAX. VERB + YOU/YOUR."
    }}
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.15,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        # v4.1 Atomic Fix
        content = content.replace("```json", "").replace("
```", "").strip()
        if not content.startswith('{'):
            content = content[content.find('{'):]
            
        return json.loads(content)
        
    except Exception as e:
        logger.error(f"Error generating script: {e}")
        return {"error": "Failed", "details": str(e)}

def pick_topic_for_run():
    return random.choice(TOPIC_POOL)["topic"]

if __name__ == "__main__":
    sample_topic = pick_topic_for_run()
    print(f"Generating for: {sample_topic}")
    result = generate_script(sample_topic)
    print(json.dumps(result, indent=4))
