"""
judge.py — Section 3.
Scores a story on a rubric and returns structured feedback the reviser can use.
Returns: (overall_score, is_safe, feedback, scores_dict)
"""

from llm import call_json


def judge(request, story):
    data = call_json(
        f"""You are a strict children's-book editor. Score this bedtime story for
ages 5-10 on each dimension from 1 to 5 (1=poor, 3=okay, 5=excellent).

Score these dimensions, using these definitions:
- age_fit: Are the vocabulary, sentence length, and themes right for ages 5-10?
  (Simple words and short sentences score high; complex or babyish ones score low.)
- safety: Is it free of anything scary or inappropriate for young children
  (violence, death, real peril, cruelty, frightening imagery, adult themes)?
  5 = completely safe and gentle; 1 = clearly unsafe.
- arc: Does it have a clear, satisfying story structure — a beginning that sets
  up a character/goal, a gentle middle challenge, and a happy resolution with a
  warm lesson? 5 = complete, well-paced arc; 1 = rambling or no real story.
- engagement: Is it charming, imaginative, and fun to read aloud, with a
  lovable character a child would care about? 5 = delightful; 1 = dull/flat.
- length: Is it the right length for a bedtime story (~400-600 words / a few
  minutes to read aloud)? 5 = just right; 1 = far too short or too long.

Request: "{request}"
STORY:
{story}

Also flag any unsafe content for young children.

Return JSON (use these exact keys):
{{"scores": {{"age_fit": 0, "safety": 0, "arc": 0, "engagement": 0, "length": 0}},
  "is_safe": true,
  "feedback": "2-3 specific, actionable suggestions, related to the score categories,for the writer to improve the story's scores if less than 5"}}""",
        temperature=0,
    )
    scores = data.get("scores", {}) or {}
    nums = [v for v in scores.values() if isinstance(v, (int, float))]
    overall = round(sum(nums) / len(nums), 2) if nums else 0.0

    # The numeric "safety" score is far more reliable than the separate is_safe
    # boolean (the model sometimes returns is_safe=false while scoring safety=5).
    # So gate on the score: unsafe only if safety is genuinely low (< 4). Fall
    # back to the boolean flag only if no numeric safety score was returned.
    safety = scores.get("safety")
    if isinstance(safety, (int, float)):
        is_safe = safety >= 4
    else:
        is_safe = bool(data.get("is_safe", True))

    return overall, is_safe, data.get("feedback", ""), scores
