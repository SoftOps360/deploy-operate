"""Step 1 - the service logic with no web server. health() + retrieval run with no key.

Before you Dockerize, prove the thing you're shipping actually works. health() must be cheap
(no model call) so orchestrators can poll it often; answer() grounds on the runbooks.
"""
import _service

print("health():", _service.health())          # no model call

# answer() without a key still does the retrieval + refusal path deterministically:
hits, refuse = _service._index().search("disk full no space", 1)[0], False
print("retrieval for 'disk full no space' ->", hits[1]["source"], f"({hits[0]:.2f})")

print("\nhealth() is a cheap liveness check (no LLM) - exactly what a Docker/K8s healthcheck needs. "
      "Add GROQ_API_KEY and hit POST /ask for a full grounded answer.")
