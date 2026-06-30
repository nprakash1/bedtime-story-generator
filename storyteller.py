"""
storyteller.py — Section 2 (and the Reviser), now STATEFUL.

The Storyteller keeps a running conversation (`self.messages`) so it remembers
every prior draft and every note. This fixes the "whack-a-mole" regression where
a revision that fixed one dimension (e.g. safety) would later reintroduce the
problem, because the writer can now see its full history and is explicitly told
to preserve what already works.

The judge stays stateless (see judge.py) so it scores each draft objectively.
"""

from llm import call_chat
from classifier import CATEGORIES

SYSTEM = (
    "You are a beloved children's bedtime storyteller for ages 5-10. Stories are "
    "SAFE (no violence, death, or scary content), use simple words and short "
    "sentences, follow a clear arc (setup -> gentle challenge -> happy resolution "
    "with a warm lesson), feel cozy and calming, and end softly for sleep."
)

# Keep the thread from growing unbounded: cap how many past turns we retain
# (the system message is always kept). Plenty for a few drafts + user edits.
MAX_TURNS = 12


class Storyteller:
    """A writing agent with memory of the whole session's drafts and feedback."""

    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM}]

    def _ask(self, user_text, temperature=0.8):
        self.messages.append({"role": "user", "content": user_text})
        reply = call_chat(self.messages, temperature=temperature)
        self.messages.append({"role": "assistant", "content": reply})
        self._trim()
        return reply

    def _trim(self):
        # Always keep the system message; keep only the most recent MAX_TURNS.
        if len(self.messages) > MAX_TURNS + 1:
            self.messages = self.messages[:1] + self.messages[-MAX_TURNS:]

    def tell(self, request, category):
        """Write the first draft from a category-tailored prompt."""
        return self._ask(
            f"""Write a bedtime story (~400-600 words) for the request: "{request}".
Style for this category ({category}): {CATEGORIES[category]}
Start with the title on its own line, use short read-aloud paragraphs, and end
calmly to ease the child toward sleep."""
        )

    def revise(self, feedback, scores=None, temperature=0.8):
        """Revise the latest draft. Because the whole conversation is in memory,
        the writer already sees every prior draft + note, so we instruct it to
        KEEP what already scores well and only improve the weak area.

        `temperature` is set by the caller via a quality-adaptive schedule:
        low scores -> high temp (explore a bold rewrite), high scores -> low
        temp (make a tiny, safe edit instead of re-rolling a good draft)."""
        focus = ""
        numeric = {k: v for k, v in (scores or {}).items() if isinstance(v, (int, float))}
        if numeric:
            lowest = min(numeric, key=numeric.get)
            breakdown = ", ".join(f"{k}={v}" for k, v in numeric.items())
            focus = (
                f"\nJudge's score breakdown (1-5): {breakdown}\n"
                f"The WEAKEST dimension is '{lowest}' ({numeric[lowest]}/5) — "
                f"prioritize improving that one."
            )
        return self._ask(
            f"""Revise YOUR most recent story to address the editor's notes below.
IMPORTANT: keep everything that already works — do NOT lower any dimension, and
NEVER reduce safety or reintroduce conflict/violence/aggression. Improve only
what's needed.

Editor notes: {feedback}{focus}

Return only the improved story (title + body).""",
            temperature=temperature,
        )

    def apply_user_request(self, note):
        """Apply a free-form change requested by the user (same memory thread)."""
        return self._ask(
            f"""The listener wants this change to YOUR most recent story: "{note}".
Apply it while keeping the story safe and age-appropriate for ages 5-10, and
keep everything else that already works. Return only the updated story."""
        )
