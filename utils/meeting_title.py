from utils.groq_client import ask_groq


def generate_meeting_title(transcript_excerpt, context="", model=None):
    context_line = f"Meeting context: {context}\n\n" if context else ""
    prompt = f"""{context_line}Read this meeting transcript excerpt and write a short, clear title for the meeting, under 10 words. Respond with only the title, nothing else.

Transcript excerpt:
\"\"\"
{transcript_excerpt}
\"\"\"
"""
    title = ask_groq(prompt, temperature=0.4, max_tokens=30, model=model)
    return title.strip().strip('"')
