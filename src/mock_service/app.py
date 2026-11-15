"""Gadai Simulasi mock business service (M0 skeleton).

Owns: the five transactional tools, SQLite storage, audit JSONL.
Track A replaces this stub with the real service.
"""

from fastapi import FastAPI

app = FastAPI(title="Gadai Simulasi mock service", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
