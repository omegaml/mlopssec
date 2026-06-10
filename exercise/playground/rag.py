import os

DATA_FOLDER = "playground/data"
MAX_LEN = 300

def retrieve(prompt: str, top_k: int = 3, min_score=3, folder=None):
    """
    Very simple retrieval:
    - scans all .txt files
    - checks if any prompt words appear in file content
    - returns matching snippets
    """
    prompt_terms = set(prompt.lower().split())
    folder = folder or DATA_FOLDER
    results = []
    # search all files
    # -- not very efficient or accurate
    # -- good enough for demonstration
    # -- instead of term matches, we could use embeddings to compute cosine similarity
    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(folder, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            content_lower = content.lower()
            # simple scoring: count term matches
            score = sum(1 for term in prompt_terms if term in content_lower)
            if score >= min_score:
                match = (score, filename, content[:MAX_LEN])
                results.append(match)
        except Exception:
            continue
    # sort by relevance
    results.sort(reverse=True, key=lambda x: x[0])
    return results[:top_k] if results else []


def extend_prompt(prompt):
    """
    This augments the prompt by documents for simple RAG functionality
    """
    documents = retrieve(prompt)
    if documents:
        prompt += '\n\nConsider the following documents:'
        for rag_score, rag_filename, rag_content in documents:
            prompt += f"\n- Document {rag_filename}: {rag_content}"
        prompt += '\n\n'
    return prompt