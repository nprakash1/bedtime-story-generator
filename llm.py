"""
llm.py — shared OpenAI helpers used by every section.
The model is fixed to gpt-3.5-turbo (assignment rule); the key comes from the
OPENAI_API_KEY env var and is never committed.
"""

import os
import json

import openai

MODEL = "gpt-3.5-turbo"


def call_model(prompt, system=None, temperature=0.7, json_mode=False):
    """One chat completion -> text. json_mode nudges a strict-JSON reply."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if json_mode:
        prompt += "\n\nReply with ONLY valid JSON (no prose, no code fences)."
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
    resp = openai.ChatCompletion.create(
        model=MODEL, messages=messages, temperature=temperature, max_tokens=1200,
    )
    return resp.choices[0].message["content"]  # type: ignore


def call_json(prompt, **kw):
    """call_model + tolerant JSON parsing (handles stray prose / code fences)."""
    raw = call_model(prompt, json_mode=True, **kw).strip()
    try:
        return json.loads(raw)
    except Exception:
        s, e = raw.find("{"), raw.rfind("}")
        try:
            return json.loads(raw[s:e + 1])
        except Exception:
            return {}
