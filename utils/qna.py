from utils.groq_client import ask_groq, MAX_TRANSCRIPT_CHARS
from utils.chunking import chunk_text, top_relevant_chunks


def answer_question(transcript, question, model=None):
    if not transcript or not transcript.strip():
        return "No transcript available to answer questions from."

    if not question or not question.strip():
        return "Please enter a question."

    chunks = chunk_text(transcript, MAX_TRANSCRIPT_CHARS)

    if len(chunks) == 1:
        context = chunks[0]
    else:
        relevant = top_relevant_chunks(chunks, question, top_n=2)
        context = "\n\n".join(relevant)

    prompt = f"""Answer the question using only the meeting transcript below.
If the answer isn't in the transcript, say "This wasn't mentioned in the meeting."
Don't make anything up.

Transcript:
\"\"\"
{context}
\"\"\"

Question: {question}

Answer:"""

    answer = ask_groq(prompt, temperature=0.1, max_tokens=800, model=model)

    if not answer.strip():
        return "No answer could be generated for this question. Try rephrasing it as a full question."

    return answer