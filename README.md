# Bedtime Story Generator — Solution

Turns any simple request into a safe, age-appropriate (ages 5–10) bedtime story
using an **LLM judge** in a tight feedback loop. One module per section:
`classifier.py`, `storyteller.py` (+ reviser), `judge.py`, shared `llm.py`
helpers, and `main.py` (orchestration + user feedback).

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
        │ 2. Storyteller  │  → generates story using a category-tailored
        └─────────────────┘     prompt + story-arc structure
                 │
                 ▼
        ┌─────────────────┐
        │    3. Judge     │  → scores rubric (age-fit, safety, arc,
        └─────────────────┘     engagement, length) → JSON + feedback
                 │
                 ├── score ≥ threshold ──► ✅ Final story → User
                 │                              │
                 │                              ▼
                 │                    5. User feedback? ("make it shorter",
                 │                       "add a dragon") ──► Reviser ──► Judge
                 │
                 └── score < threshold ──► 4. Reviser (feeds judge notes
                                              back to storyteller, loops
                                              up to N times) ──► back to Judge
```


### Run it
```bash
pip install "openai<1.0"
export OPENAI_API_KEY=sk-...          # your own key; never commit it

python main.py                                # interactive
python main.py "a brave little turtle"        # one-shot
```

> Model is fixed to `gpt-3.5-turbo`; the key is read from `OPENAI_API_KEY`.
> The judge scores every draft 1–5 across a rubric and feeds actionable notes
> back to the storyteller until the story clears the bar (or hits the loop cap).

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