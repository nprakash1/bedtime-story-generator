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

FEEDBACK RULE: If ANY dimension scores below 5, you MUST give 2-3 specific,
actionable suggestions that target the lowest-scoring dimension(s) so the writer
can raise those scores. Return "N/A" for feedback ONLY if every dimension is
exactly 5.

Return JSON (use these exact keys):
{{"scores": {{"age_fit": 0, "safety": 0, "arc": 0, "engagement": 0, "length": 0}},
  "is_safe": true,
  "feedback": "2-3 specific, actionable suggestions targeting the lowest dimension(s), or \\"N/A\\" only if all dimensions are 5"}}""",

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

    # Belt-and-suspenders: even with the explicit FEEDBACK RULE above, the model
    # sometimes returns empty/"N/A" feedback while a dimension is still < 5. In
    # that case, synthesize actionable feedback that names the weakest
    # dimension(s) so the reviser always has something concrete to act on.
    feedback = (data.get("feedback") or "").strip()
    below = {k: v for k, v in scores.items()
             if isinstance(v, (int, float)) and v < 5}
    if below and feedback.lower() in ("", "n/a", "na", "none"):
        weakest = ", ".join(f"{k} ({v}/5)" for k, v in sorted(below.items(),
                                                              key=lambda kv: kv[1]))
        feedback = f"Improve the weakest dimension(s): {weakest}."

    return overall, is_safe, feedback, scores
