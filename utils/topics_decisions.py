from utils.groq_client import ask_groq, safe_json_loads, MAX_TRANSCRIPT_CHARS
from utils.chunking import chunk_text


def _extract_from_chunk(chunk, context="", model=None):
    context_line = f"Meeting context: {context}\n\n" if context else ""
    prompt = f"""{context_line}Analyze this section of a meeting transcript.

Identify:
- topics: short titles with a 1-2 sentence summary of what was discussed
- decisions: clear, concrete decisions that were made (empty list if none)

Respond with a JSON object in this exact shape:
{{"topics": [{{"title": "...", "summary": "..."}}], "decisions": ["..."]}}

If nothing applies, use empty lists for either field.

Transcript:
\"\"\"
{chunk}
\"\"\"
"""
    raw = ask_groq(prompt, temperature=0.2, max_tokens=1200, json_mode=True, model=model)
    parsed = safe_json_loads(raw)

    if isinstance(parsed, dict):
        return parsed.get("topics", []), parsed.get("decisions", [])
    return [], []


def extract_topics_and_decisions(transcript, context="", model=None):
    if not transcript or not transcript.strip():
        return {"topics": [], "decisions": []}

    chunks = chunk_text(transcript, MAX_TRANSCRIPT_CHARS)
    all_topics = []
    all_decisions = []

    for chunk in chunks:
        topics, decisions = _extract_from_chunk(chunk, context=context, model=model)
        all_topics.extend(topics)
        all_decisions.extend(decisions)

    return {"topics": all_topics, "decisions": all_decisions}
