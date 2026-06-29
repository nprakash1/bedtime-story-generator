"""
Bedtime Story Generator (Hippocratic AI take-home) — orchestration.

Pipeline:  Classifier -> Storyteller -> Judge -> (Reviser loop) -> Final story

    classifier.classify  -> storyteller.tell -> judge.judge
      -> score >= threshold ? ship it
                            : storyteller.revise(judge feedback), loop up to N
                              times, then re-judge. Return the best safe draft.
    Then the USER can request changes, which re-runs the reviser + judge.

Run:
    export OPENAI_API_KEY=sk-...      # your own key; never commit it
    python main.py
    python main.py "a brave little turtle who is afraid of the water"

------------------------------------------------------------------------------
WHAT I'D BUILD NEXT (with 2 more hours):
  - A small eval harness to score prompt variants on sample requests (a
    regression test for prompt tweaks), and lightweight memory so recurring
    characters / the child's name persist across sessions.
------------------------------------------------------------------------------
"""

import os
import sys

from classifier import classify
from storyteller import tell, revise
from judge import judge

PASS_THRESHOLD = 4.3     # avg rubric score (out of 5) needed to ship
MAX_ITERATIONS = 3       # storyteller drafts before returning the best effort


def generate_story(request):
    category = classify(request)
    print(f"  category: {category}")
    story = tell(request, category)

    best_story, best_score, best_safe = story, 0.0, False
    for i in range(1, MAX_ITERATIONS + 1):
        score, is_safe, feedback, scores = judge(request, story)
        print(f"  draft {i}: score {score}/5  safe={is_safe}  {scores}")
        if feedback:
            print(f"    judge feedback: {feedback}")
        # Always keep the best draft: prefer safe ones, then higher score. This
        # guarantees we return a real story/score even if none is flagged safe.
        if (is_safe, score) > (best_safe, best_score):
            best_story, best_score, best_safe = story, score, is_safe
        if is_safe and score >= PASS_THRESHOLD:
            break
        if i < MAX_ITERATIONS:
            print("  revising with judge feedback...")
            story = revise(request, story, feedback, scores)

    return best_story, best_score


def main():
    request = " ".join(sys.argv[1:]) or \
        input("What kind of story do you want to hear? ").strip() or \
        "A story about a girl named Alice and her best friend Bob, who is a cat."

    if not os.getenv("OPENAI_API_KEY"):
        print("Set your key first:  export OPENAI_API_KEY=sk-...")
        return

    print("Building your story...")
    story, score = generate_story(request)
    _show(story, score)

    # Let the user provide feedback / request changes (re-uses the reviser).
    while True:
        try:
            note = input(
                "\nPress Enter to finish, or type a change "
                "(e.g. 'make it shorter', 'add a friendly dragon'): "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSweet dreams! 🌙")
            break
        if not note:
            print("\nSweet dreams! 🌙")
            break
        print("Revising with your request...")
        story = revise(request, story, note)
        score, _, _, _ = judge(request, story)  # re-score the user-edited version
        _show(story, score)


def _show(story, score):
    print("\n" + "=" * 60)
    print(story.strip())
    print("=" * 60)
    print(f"(quality score: {score}/5)")


if __name__ == "__main__":
    main()
