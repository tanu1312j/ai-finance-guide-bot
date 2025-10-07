# AI Investment Advisor — Starter (Single-Agent, Tools, Memory, Guardrails)

A production-friendly starter you can finish in ~4 hours. It wires up:
- **Single-agent** tool-calling workflow (easiest to ship fast; extensible to multi-agent).
- **Two custom ML tools** (Savings Calculator, Insurance Recommender) — plug your models in `app/tools/`.
- **Memory**: profile store (JSON) + short conversation buffer.
- **Guardrails**: input validation, PII minimization, disclaimers, safe response policies.
- **LLM backend**: switch between **Amazon Bedrock** or **OpenAI** with a config flag.
- **Chatbot UIs**: Streamlit chat or FastAPI API.

---

## Quick Start

### 0) Choose your LLM backend
- **Amazon Bedrock (recommended if you already have AWS set up):**
  - Enable a chat model in Bedrock (e.g., Anthropic Claude 3 Sonnet).
  - Set `provider: bedrock` and `bedrock.model_id` in `config.yaml`.
  - Export AWS creds via env or profile.

- **OpenAI (simple if you have an API key):**
  - Set `provider: openai` and `openai.model` in `config.yaml`.
  - Export `OPENAI_API_KEY`.

### 1) Install
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
cp .env.example .env
```

### 2) Run Streamlit (chatbot UI)
```bash
streamlit run ui/streamlit_app.py
```

### 3) Or run FastAPI
```bash
uvicorn app.server:app --reload --port 8000
# POST /chat with {"user_id":"user123","message":"What insurance do I need?"}
```

---

## Where to plug your models

- Savings model: `app/tools/savings_model.py` → replace `predict_savings_amount()` with your model call.
- Insurance model: `app/tools/insurance_model.py` → replace `recommend_insurance()` with your model call.
- Both receive a `demographics: dict` (age, marital_status, dependents, income, net_worth, etc.).

---

## Files
```
app/
  agent.py            # Build the single-agent with tools + memory + policies
  memory.py           # Conversation buffer + profile store (JSON)
  guardrails.py       # Validators, PII scrubbing, disclaimers
  prompts.py          # System instructions for the agent
  server.py           # FastAPI app exposing /chat and direct tool endpoints
  tools/
    savings_model.py  # ⟵ plug your savings ML model here
    insurance_model.py# ⟵ plug your insurance ML model here
    profile_store.py  # read/write the user's long-lived profile
    market.py         # simple market snapshot (stub/demo)
ui/
  streamlit_app.py    # Streamlit chatbot with buttons/forms for use cases
config.example.yaml   # Provider config (bedrock/openai) and defaults
.env.example          # Example env vars
requirements.txt
README.md
```

---

## Suggested 4-hour plan

1. **(60 min)** Wire your ML models in `app/tools/*.py` and test their functions directly.
2. **(45 min)** Tweak `prompts.py` (tone, guardrails) + `config.yaml` (provider, model IDs).
3. **(30 min)** Launch Streamlit UI; test *Savings* and *Insurance* flows.
4. **(30 min)** Add your demographics fields; confirm profile memory persists across chat.
5. **(30 min)** Add any domain checks to `guardrails.py` (e.g., min income, age ranges).
6. **(45 min)** (Optional) Run FastAPI and integrate with your existing frontend.

Ship the MVP. Iterate later with multi-agent (add a routing graph in `agent.py`).

---

## Tracing & Logs
- Set env `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` to use LangSmith (optional).
- Local logs print to console; FastAPI also logs requests/responses.
