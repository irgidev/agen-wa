"""WhatsApp webhook application (M0 skeleton).

Owns: GET /webhook (Meta verification handshake), POST /webhook (signed
message intake), outbound replies. Track B extends this module.
"""

from fastapi import FastAPI

app = FastAPI(title="agen-wa webhook", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
