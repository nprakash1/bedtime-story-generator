"""
classifier.py — Section 1.
Categorizes the request so the storyteller can use a tailored strategy.
"""

from llm import call_json

# Category -> tailored generation strategy (injected into the storyteller).
CATEGORIES = {
    "adventure": "Gentle excitement with a clear goal and a safe, satisfying resolution.",
    "animal": "Warm animal friendships, simple dialogue, and a kind lesson.",
    "calm": "Soothing, slow, lullaby-like pacing that winds down toward sleep.",
    "educational": "Teach ONE simple idea naturally through the story, never lecturing.",
    "fantasy": "Gentle magic and wonder; any 'villain' is silly, never scary.",
}


def classify(request):
    data = call_json(
        f"""Categorize this children's bedtime story request into exactly one of:
{", ".join(CATEGORIES)}.
Request: "{request}"
Return JSON: {{"category": "<one>"}}""",
        temperature=0,
    )
    cat = data.get("category", "calm")
    return cat if cat in CATEGORIES else "calm"
