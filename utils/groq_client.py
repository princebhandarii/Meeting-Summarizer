import json
import os
from groq import Groq

DEFAULT_MODEL = "openai/gpt-oss-20b"
MAX_TRANSCRIPT_CHARS = 9000
AVAILABLE_LLM_MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]

_client = None


def get_groq_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Add it to your .env file. "
                "Get a free key at https://console.groq.com/keys"
            )
        _client = Groq(api_key=api_key)
    return _client


def ask_groq(prompt, temperature=0.3, max_tokens=800, json_mode=False, model=None):
    client = get_groq_client()
    kwargs = dict(
        model=model or DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
    except Exception:
        kwargs.pop("response_format", None)
        response = client.chat.completions.create(**kwargs)

    return response.choices[0].message.content.strip()


def safe_json_loads(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    for open_ch, close_ch in [("{", "}"), ("[", "]")]:
        start = text.find(open_ch)
        end = text.rfind(close_ch)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                continue

    return None
