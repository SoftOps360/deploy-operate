"""The RAG service as an HTTP API (FastAPI). Two endpoints:

  GET  /health      -> liveness/readiness (no model call) - for Docker/K8s health checks & LBs
  POST /ask {"question": "..."} -> a grounded, cited answer from the runbooks

Run locally:   uvicorn app:app --host 0.0.0.0 --port 8000
Then:          curl localhost:8000/health
               curl -X POST localhost:8000/ask -H "content-type: application/json" -d '{"question":"disk full?"}'
"""
from fastapi import FastAPI
from pydantic import BaseModel

import _service

app = FastAPI(title="ask-runbook", version="1.0")


class Ask(BaseModel):
    question: str


@app.get("/health")
def health():
    return _service.health()


@app.post("/ask")
def ask(body: Ask):
    return _service.answer(body.question)
