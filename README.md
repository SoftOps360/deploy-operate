# Episode 20 — Deploy & Operate the AI App

We've built plenty of AI tools. Now ship one like a real service: wrap it in an **HTTP API**,
put it in a **Docker image**, give it a **health check**, and run it with **docker compose**.
This funnels straight into the channel's **Docker & AWS** series — from there you deploy it to
the cloud exactly like any other container.

## What we ship

The `ask-runbook` RAG service (from Episodes 9–10) as a small FastAPI app:

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness/readiness — **no model call**, so orchestrators can poll it cheaply. |
| `POST /ask` `{"question": "..."}` | A grounded, cited answer from the runbooks. |

Keeping the **logic in `_service.py`** (separate from FastAPI) means it's testable with no server
— same "brains vs plumbing" split as the Slack episode.

## Files

| File | What it is |
|------|-----------|
| `app.py` | FastAPI app: `/health` + `/ask`. |
| `_service.py` | The logic: `health()` (no LLM) + `answer()` (RAG). |
| `Dockerfile` | `python:3.11-slim`, deps cached, **non-root user**, uvicorn. |
| `docker-compose.yml` | Service + port + **healthcheck** + `restart: unless-stopped`. |
| `.dockerignore` | Keeps the image small and secrets out. |
| `01_service_logic.py` | Prove `health()` + retrieval work before you build the image. |

## Run it

```bash
# locally (no Docker):
pip install -r requirements.txt
uvicorn app:app --port 8000
curl localhost:8000/health
curl -X POST localhost:8000/ask -H "content-type: application/json" -d "{\"question\":\"disk full?\"}"

# with Docker:
export GROQ_API_KEY=gsk_...        # Windows: set GROQ_API_KEY=gsk_...
docker compose up --build
```

Then deploy the image to your cloud the same way as any container — that's the **Docker/AWS
series**. The health check lets a load balancer / Kubernetes know when the app is ready.

## How it was verified

FastAPI/uvicorn aren't installed in the authoring sandbox, so the live server isn't started
here. What is verified: everything **compiles**, `_service.health()` returns `ok` with 24 chunks
**without any model call**, retrieval grounds correctly (`disk full → disk-full.md`), and the
compose file defines the service + health check. Install the deps and run `uvicorn`/`docker
compose` to serve it.

## Honesty & limits (please keep these in the video)

- **Secrets at runtime, never in the image.** The `Dockerfile` bakes no key; `docker-compose.yml`
  passes `GROQ_API_KEY` from your environment. Baking secrets into an image leaks them to anyone
  who can pull it. `.env` and `.git` are in `.dockerignore`.
- **`/health` must stay cheap.** It deliberately does **not** call the model — a health check that
  costs money or hits a flaky dependency will flap and cause restart storms.
- **This isn't production-hardened yet.** Add rate limiting, timeouts (Episode 19), auth on the
  endpoint, and the guardrails (Episode 13) before exposing anything that can act. A public `/ask`
  is a cost and prompt-injection surface (Episode 21).
- **Right-size it.** A RAG service is light; an agent doing many model calls per request needs
  concurrency, timeouts, and cost limits thought through before it faces real traffic.
- **Image + library versions drift.** Pin base image and dependency versions for reproducible
  builds; rebuild to pick up security patches.
