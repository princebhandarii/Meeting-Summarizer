def chunk_text(text, max_chars=9000):
    words = text.split()
    chunks = []
    current = []
    current_len = 0

    for word in words:
        current.append(word)
        current_len += len(word) + 1
        if current_len >= max_chars:
            chunks.append(" ".join(current))
            current = []
            current_len = 0

    if current:
        chunks.append(" ".join(current))

    return chunks


def score_chunk_relevance(chunk, question):
    q_words = {w.lower().strip("?.,!") for w in question.split() if len(w) > 3}
    chunk_words = chunk.lower().split()
    return sum(1 for w in chunk_words if w.strip("?.,!") in q_words)


def top_relevant_chunks(chunks, question, top_n=2):
    scored = [(score_chunk_relevance(c, question), c) for c in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_n]]
