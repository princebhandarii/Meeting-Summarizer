from utils.groq_client import ask_groq, MAX_TRANSCRIPT_CHARS
from utils.chunking import chunk_text


def _summarize_piece(text, is_final_pass=False, context="", model=None):
    context_line = f"Meeting context: {context}\n\n" if context else ""

    if is_final_pass:
        prompt = f"""{context_line}Combine these partial meeting summaries into one clear, well-organized summary.
Cover what the meeting was about, the main points, and the outcomes. Keep it concise.

Partial summaries:
\"\"\"
{text}
\"\"\"
"""
    else:
        prompt = f"""{context_line}Summarize this part of a meeting transcript into key points and decisions.
Keep it factual, no extra commentary.

Transcript section:
\"\"\"
{text}
\"\"\"
"""
    return ask_groq(prompt, temperature=0.3, max_tokens=500, model=model)


def generate_summary(transcript, context="", model=None):
    if not transcript or not transcript.strip():
        return "No transcript available to summarize."

    chunks = chunk_text(transcript, MAX_TRANSCRIPT_CHARS)

    if len(chunks) == 1:
        return _summarize_piece(chunks[0], context=context, model=model)

    partial_summaries = [_summarize_piece(c, context=context, model=model) for c in chunks]
    combined = "\n\n".join(partial_summaries)
    return _summarize_piece(combined, is_final_pass=True, context=context, model=model)
