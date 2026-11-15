# agen-wa

Transactional WhatsApp agent with governance, an audit log, and human handoff, built on the WhatsApp Business Cloud API. The agent executes work (pawnshop-style transactions on a simulated business) instead of only answering questions. Part of a five-project Indonesian NLP portfolio; this project mirrors the operational profile of an official WhatsApp BSP: every tool call is audited, high-risk actions require operator approval, and conversations can be escalated to a human operator with full context.

Simulated business: **Gadai Simulasi** (pawnshop simulation: collateral estimate, loan application, payment status, simulated payment, branch appointment). All data is local mock data. There is no real money and no external financial API.

## Problem

WhatsApp agents in production fail in ways demos never show: an LLM calls a transactional tool with wrong arguments and there is no record of what happened; a user asks for a loan above policy and the system has no approval path; a conversation gets stuck and no human ever sees the transcript. This repo treats those as first-class requirements: an append-only audit trail for every tool call, a policy engine that queues high-risk actions for operator approval, and an operator console that receives escalated conversations with the transcript attached.

## Approach

- **Channel**: WhatsApp Business Cloud API in developer mode (Meta test number). Inbound webhook with `x-hub-signature-256` verification, outbound replies via the Graph API.
- **Agent core**: model-agnostic LLM layer (OpenAI-compatible, Gemini, Ollama local) with function calling, plus a deterministic rule-based fallback so tests and evaluation runs do not require an API key. Conversation state machine: `greeting -> inquiring -> awaiting_approval -> handoff -> done`, with session timeout and reset.
- **Mock service**: FastAPI + SQLite exposing five transactional tools: `estimate_collateral`, `create_loan`, `get_payment_status`, `book_appointment`, `cancel_appointment`. Every call is appended to an audit JSONL file.
- **Governance**: policy engine marks high-risk tool calls (e.g. `create_loan` above the approval threshold) as requiring approval. The call is not executed until an operator approves or rejects it in the operator console; the decision is audited and the user is notified on WhatsApp.
- **Human handoff**: an explicit escalation creates an operator ticket with the transcript and a context summary. The agent stays silent until the operator closes the ticket.
- **Evaluation**: a scripted scenario suite (JSON) runs the agent against the mock service without WhatsApp. The harness reports tool-call accuracy, argument correctness, governance violations (target: zero), and handoff rate. Numbers in this README come only from committed harness reports, with the run date and suite version.

## Status

| Milestone | Scope | Status |
|---|---|---|
| M0 | Skeleton, CI, docker-compose, README | done |
| M1 | Mock service, five tools, audit JSONL, scenario suite v1 | in progress |
| M2 | Live WhatsApp loop with Meta test number, signature verification | blocked on Meta developer setup (see Setup) |
| M3 | Governance engine, approval flow, operator console, handoff, scenario suite v2 | in progress |
| M4 | Final README with sequence diagram and evaluation results, tag `v0.1.0` | planned |

## Evaluation

Results are published here only after real harness runs. Each run lists: suite version, agent mode (rule-based or LLM with provider and model), run date, and the metrics: tool-call accuracy, argument accuracy, governance violations, handoff rate. No numbers appear in this README before a committed report backs them.

## Setup

### Prerequisites

- Python 3.13+ (development uses 3.14)
- Docker with compose (optional, for the full stack)
- A Meta developer account and a WhatsApp test number (Part A below)
- For M2: a public HTTPS tunnel for the webhook (cloudflared or ngrok)

### Part A — Meta developer account and test number (needed before M2)

1. Go to [developers.facebook.com](https://developers.facebook.com) and log in with your Facebook account. Complete account verification if prompted (phone or email confirmation).
2. Click **My Apps** in the top right, then **Create App**. Choose a use case (pick **Other** / business-type app if asked), give the app any name (e.g. `agen-wa-dev`), and provide a contact email.
3. On the app dashboard, find the **Add products to your app** section and click **Set up** on the **WhatsApp** product card.
4. In the left menu under WhatsApp, open **API Setup**. Meta provisions a **test number** automatically. Note down three values from this page:
   - **Test phone number** (the `From` number, e.g. `+1 555 123 4567`)
   - **Phone number ID** (a long numeric ID)
   - **WhatsApp Business Account ID**
5. Still on **API Setup**, click **Generate access token**. This temporary token is valid for about 24 hours. For development across several days, create a longer-lived token instead: go to [business.facebook.com/business/settings](https://business.facebook.com/business/settings), open **Users > System users**, create a system user with the **Admin** role, click **Generate token**, select your app, and add the `whatsapp_business_messaging` and `whatsapp_business_management` permissions. Copy the token.
6. On **API Setup**, find the **To** dropdown, click **Manage phone number list**, and add your personal WhatsApp number. Verify it with the code Meta sends to your WhatsApp. You can register up to 5 recipient numbers on a test number; only these can exchange messages with the agent.
7. Verify the token works from a terminal (replace `<TOKEN>` and `<PHONE_NUMBER_ID>`):

   ```bash
   curl -X GET "https://graph.facebook.com/v23.0/<PHONE_NUMBER_ID>?fields=verified_name&access_token=<TOKEN>"
   ```

   A JSON response with `verified_name` means the credentials are working. If you get an OAuth error, regenerate the token.
8. From the app dashboard, open **App Settings > Basic** and copy the **App Secret**. This is used to verify webhook signatures (`x-hub-signature-256`).
9. Create your local environment file:

   ```bash
   cp .env.example .env
   ```

   Then fill in: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_APP_SECRET`, and choose any random string for `WHATSAPP_VERIFY_TOKEN` (you invent it; Meta will just echo it during webhook verification).

### Part B — Webhook wiring (done when M2 code lands)

1. Start the stack: `docker compose up --build`.
2. Expose it publicly: `cloudflared tunnel --url http://localhost:8000` (no account needed) or `ngrok http 8000`.
3. In the app dashboard, open WhatsApp > **Configuration**. Set **Callback URL** to `https://<your-tunnel>/webhook` and **Verify token** to the exact value of `WHATSAPP_VERIFY_TOKEN` from `.env`. Click **Verify and save**; the webhook responds to Meta's verification handshake.
4. Under **Webhook fields**, subscribe to the `messages` field.
5. Send any WhatsApp message from your verified recipient number to the test number. The agent should reply. (This step works once M2 is merged; until then the webhook only answers the verification handshake and `/healthz`.)

### Local development

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows; use .venv/bin on Linux/macOS
.venv/Scripts/python -m pytest -q
.venv/Scripts/python -m ruff check .
```

### Docker

```bash
cp .env.example .env   # fill values before docker compose
docker compose up --build
# webhook:      http://localhost:8000/healthz
# mock service: http://localhost:8001/healthz
# operator console (M3): http://localhost:8002
```

## Repository layout

```
src/agent/            agent core: nlu_tools (model-agnostic LLM layer), session (FSM), governance
src/mock_service/     FastAPI + SQLite mock business service and tools
src/webhook/          WhatsApp webhook app (verification, signature check, idempotency, replies)
src/harness/          scenario evaluation harness
operator_console/     operator console (approvals + handoff tickets)
scenarios/            scripted scenario suite (JSON)
tests/                unit and integration tests (WhatsApp API mocked)
reports/              committed harness run reports
audit/                runtime audit JSONL (gitignored)
```

## Privacy design notes

- The audit log records the sender's WhatsApp ID, tool name, arguments, result, and decision. Message bodies are not written verbatim to the audit log.
- The handoff feature is the one place a transcript is stored and shown (to the operator), because the operator cannot act without it. This exception is deliberate and documented.
- Secrets live only in `.env`, which is gitignored. No tokens are committed anywhere in this repository.

## Limitations

- The Meta test number can only exchange messages with up to 5 pre-verified recipient numbers; this is a developer-mode constraint, not an agent limitation.
- Gadai Simulasi data is mock data generated by the seed script; amounts and collateral values are illustrative.
- Single tenant, Indonesian language only, no broadcast/template messages, no voice.

## License

MIT. See [LICENSE](LICENSE).
