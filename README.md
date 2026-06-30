# Bedtime Story Generator — Solution

Turns any simple request into a safe, age-appropriate (ages 5–10) bedtime story
using a multi-agent loop: a **classifier** picks a generation strategy, a
**storyteller** writes the story, and an **LLM judge** scores it and feeds notes
back for revision until it clears a quality bar. The user can then request
further changes interactively.

### Block diagram

```
            User request
                 │
                 ▼
        ┌─────────────────┐
        │  1. Classifier  │  → categorizes request (adventure, animal,
        └─────────────────┘     calm, educational, fantasy)
                 │
                 ▼
        ┌─────────────────┐
        │ 2. Storyteller  │  → writes story from a category-tailored
        │   (STATEFUL)    │     prompt + story-arc structure
        └─────────────────┘
                 │  draft
                 ▼
        ┌─────────────────┐
        │    3. Judge     │  → scores rubric (age_fit, safety, arc,
        │   (STATELESS)   │     engagement, length) → JSON + feedback
        └─────────────────┘
                 │
                 ├── score ≥ threshold ──► ✅ best safe draft → User
                 │                                   │
                 │                                   ▼
                 │                         5. User feedback? ("make it
                 │                            shorter", "add a dragon")
                 │                            ──► Storyteller ──► Judge
                 │
                 └── score < threshold ──► 4. Reviser = Storyteller.revise()
                                              feeds judge notes + score
                                              breakdown back, loops up to
                                              N times ──► back to Judge
```

### Key design: writer remembers, judge forgets

```
  Storyteller (STATEFUL) ── remembers every draft + note ──┐
        │  writes / revises / applies user edits            │  (one growing
        ▼                                                    │   conversation
     Judge (STATELESS) ── scores each draft fresh, no bias ──┘   thread)
```

- **Storyteller is stateful.** It keeps one conversation thread per session
  (`Storyteller.messages`), so it remembers every prior draft and note. This
  stops the "whack-a-mole" regression where a later revision reintroduces a
  problem it already fixed (e.g. making a story unsafe again). The revise prompt
  also explicitly says *keep what already works — never lower safety or
  reintroduce conflict*.
- **Judge is stateless.** It scores each draft from scratch with no history, so
  it can't be anchored/biased by earlier scores or the writer's framing.

### How it works

1. **Classifier** (`classifier.py`) — labels the request as one of five
   categories and selects a tailored generation strategy for each.
2. **Storyteller** (`storyteller.py`) — a stateful agent that writes the first
   draft, revises against judge feedback, and applies free-form user edits, all
   on the same memory thread.
3. **Judge** (`judge.py`) — a strict editor that scores 1–5 on a defined rubric
   (`age_fit, safety, arc, engagement, length`) and returns actionable feedback
   as JSON. Safety is gated on the numeric `safety` score for reliability.
4. **Orchestrator** (`main.py`) — runs classify → tell → judge, then loops
   revise → judge up to `MAX_ITERATIONS`, shipping early once the average score
   clears `PASS_THRESHOLD`. Revisions use a **quality-adaptive temperature**
   (see below). It always returns the **best safe draft** seen, then opens an
   interactive loop for user change requests.
5. **Shared LLM helpers** (`llm.py`) — `call_chat()` (history-aware, for the
   stateful writer) plus `call_model()`/`call_json()` (one-shot, for the
   stateless classifier and judge). Model fixed to `gpt-3.5-turbo`.

### Run it
```bash
pip install "openai<1.0"
export OPENAI_API_KEY=sk-...          # your own key; never commit it

python main.py                                # interactive
python main.py "a brave little turtle"        # one-shot
```

> Model is fixed to `gpt-3.5-turbo`; the key is read from `OPENAI_API_KEY`
> (never hardcoded). Each draft is scored 1–5 across the rubric and the notes
> are fed back to the storyteller until the story clears the bar (or hits the
> loop cap), after which the best safe draft is returned.

### Quality-adaptive revision temperature

Revisions don't use a fixed temperature — the reviser's sampling temperature is
set by the judge's score, so the model explores when a draft is weak and edits
conservatively when it's already good. This prevents a strong draft from being
"re-rolled" into a worse one (a real regression we observed):

- **score ≤ 2** → `0.8` (explore a fundamentally different story)
- **2 < score < 5** → linearly interpolated `0.8 → 0.6`
- **score ≥ 5** → `0.6` (still allow a little variation)

The first draft stays creative; only the targeted revisions are dampened. It's
the same idea as simulated annealing: cool down as you approach a good solution.

### What I'd build next (with 2 more hours)

1. A small eval harness that runs a fixed set of 10–15 sample requests per each of
   the 5 categories, ensuring that a thresholded score is achieved within a
   configurable number of drafts. Re-running the harness after any model changes
   ensures that the quality is maintained.

2. A lightweight cross-session memory for episodic "series" storytelling. Persist
   a small JSON "character bible" to disk that stores the child's name (asked once,
   then reused) and a name-keyed dictionary of recurring characters and settings
   with fixed traits. Each story injects the relevant entries as fixed canon and
   appends any new characters afterward without overwriting established ones.

---

# Hippocratic AI Coding Assignment
Welcome to the [Hippocratic AI](https://www.hippocraticai.com) coding assignment

## Instructions
The attached code is a simple python script skeleton. Your goal is to take any simple bedtime story request and use prompting to tell a story appropriate for ages 5 to 10.
- Incorporate a LLM judge to improve the quality of the story
- Provide a block diagram of the system you create that illustrates the flow of the prompts and the interaction between judge, storyteller, user, and any other components you add
- Do not change the openAI model that is being used. 
- Please use your own openAI key, but do not include it in your final submission.
- Otherwise, you may change any code you like or add any files

---

## Rules
- This assignment is open-ended
- You may use any resources you like with the following restrictions
   - They must be resources that would be available to you if you worked here (so no other humans, no closed AIs, no unlicensed code, etc.)
   - Allowed resources include but not limited to Stack overflow, random blogs, chatGPT et al
   - You have to be able to explain how the code works, even if chatGPT wrote it
- DO NOT PUSH THE API KEY TO GITHUB. OpenAI will automatically delete it

---

## What does "tell a story" mean?
It should be appropriate for ages 5-10. Other than that it's up to you. Here are some ideas to help get the brain-juices flowing!
- Use story arcs to tell better stories
- Allow the user to provide feedback or request changes
- Categorize the request and use a tailored generation strategy for each category

---

## How will I be evaluated
Good question. We want to know the following:
- The efficacy of the system you design to create a good story
- Are you comfortable using and writing a python script
- What kinds of prompting strategies and agent design strategies do you use
- Are the stories your tool creates good?
- Can you understand and deconstruct a problem
- Can you operate in an open-ended environment
- Can you surprise us

---

## Other FAQs
- How long should I spend on this? 
No more than 2-3 hours
- Can I change what the input is? 
Sure
- How long should the story be?
You decide
