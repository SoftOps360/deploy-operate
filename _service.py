"""Service logic, kept separate from the web framework (same idea as Ep15: brains vs plumbing).

answer() is the RAG-over-runbooks call from Episode 9; health() is a cheap liveness check that
does NOT call the model. app.py wraps these in FastAPI. Keeping them here means the logic is
testable with no server and (for health + retrieval) no key.
"""
from _rag import build_chunks, TfidfIndex

MIN_SCORE = 0.05
_INDEX = None

SYSTEM = ("You are an on-call assistant. Answer ONLY from the CONTEXT (the team's runbooks). "
          "If it isn't there, reply 'No runbook covers this.' Cite the source file like [disk-full.md].")


def _index():
    global _INDEX
    if _INDEX is None:
        _INDEX = TfidfIndex().fit(build_chunks("runbooks"))
    return _INDEX


def health():
    """Liveness/readiness: the index builds and has chunks. No model call, so it's fast & free."""
    ok = len(_index().chunks) > 0
    return {"status": "ok" if ok else "degraded", "chunks": len(_index().chunks)}


def answer(question):
    hits = _index().search(question, 3)
    if not hits or hits[0][0] < MIN_SCORE:
        return {"answer": "No runbook covers this.", "sources": []}
    from _llm import ask   # lazy: health + retrieval need no LLM
    context = "\n\n".join(f"[{c['source']} :: {c['section']}]\n{c['text']}" for _, c in hits)
    text = ask(f"CONTEXT:\n{context}\n\nQUESTION: {question}", system=SYSTEM)
    return {"answer": text, "sources": sorted({c["source"] for _, c in hits})}
