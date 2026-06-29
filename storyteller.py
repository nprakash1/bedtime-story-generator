"""
storyteller.py — Section 2 (and the Reviser).
Generates the story from a category-tailored prompt, and revises it using the
judge's feedback.
"""

from llm import call_model
from classifier import CATEGORIES

SYSTEM = (
    "You are a beloved children's bedtime storyteller for ages 5-10. Stories are "
    "SAFE (no violence, death, or scary content), use simple words and short "
    "sentences, follow a clear arc (setup -> gentle challenge -> happy resolution "
    "with a warm lesson), feel cozy and calming, and end softly for sleep."
)


def tell(request, category):
    return call_model(
        f"""Write a bedtime story (~400-600 words) for the request: "{request}".
Style for this category ({category}): {CATEGORIES[category]}
Start with the title on its own line, use short read-aloud paragraphs, and end
calmly to ease the child toward sleep.""",
        system=SYSTEM,
        temperature=0.8,
    )


def revise(request, story, feedback, scores=None):
    # If the judge gave a per-dimension breakdown, show it and point the writer
    # at the weakest dimension so the revision targets the real problem.
    focus = ""
    numeric = {k: v for k, v in (scores or {}).items() if isinstance(v, (int, float))}
    if numeric:
        lowest = min(numeric, key=numeric.get)
        breakdown = ", ".join(f"{k}={v}" for k, v in numeric.items())
        focus = (
            f"\nJudge's score breakdown (1-5): {breakdown}\n"
            f"The WEAKEST dimension is '{lowest}' ({numeric[lowest]}/5) — "
            f"prioritize improving that one.\n"
        )

    return call_model(
        f"""Revise this bedtime story to address the editor's notes. Keep what
works; change only what's needed.

Request: "{request}"
Editor notes: {feedback}{focus}
STORY:
{story}

Return only the improved story (title + body).""",
        system=SYSTEM,
        temperature=0.8,
    )
