from utils.groq_client import ask_groq, safe_json_loads, MAX_TRANSCRIPT_CHARS
from utils.chunking import chunk_text


def _extract_from_chunk(chunk, context="", model=None):
    context_line = f"Meeting context: {context}\n\n" if context else ""
    prompt = f"""{context_line}Find action items in this meeting transcript section.

For each one, give: task, assignee (use "Unassigned" if not said), deadline
(use "Not specified" if not mentioned), priority (High/Medium/Low, infer from
tone/urgency if not explicit), and status (Not Started/In Progress/Completed).

Respond with a JSON object in this exact shape:
{{"items": [{{"task": "...", "assignee": "...", "deadline": "...", "priority": "...", "status": "..."}}]}}

If there are no action items in this section, respond with {{"items": []}}.

Transcript:
\"\"\"
{chunk}
\"\"\"
"""
    raw = ask_groq(prompt, temperature=0.2, max_tokens=1200, json_mode=True, model=model)
    parsed = safe_json_loads(raw)

    if isinstance(parsed, dict):
        return parsed.get("items", [])
    if isinstance(parsed, list):
        return parsed
    return []


def extract_action_items(transcript, context="", model=None):
    if not transcript or not transcript.strip():
        return []

    chunks = chunk_text(transcript, MAX_TRANSCRIPT_CHARS)
    all_items = []
    for chunk in chunks:
        all_items.extend(_extract_from_chunk(chunk, context=context, model=model))

    return all_items
