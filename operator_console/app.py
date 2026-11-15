"""Operator console (M0 skeleton).

Owns: pending approval queue view, approve/reject actions, handoff tickets
with transcripts. Track C replaces this stub with the real console.
"""

from fastapi import FastAPI

app = FastAPI(title="agen-wa operator console", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
