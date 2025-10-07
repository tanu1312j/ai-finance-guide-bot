from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Dict, Any
from .agent import chat, _tool_savings, _tool_insurance

app = FastAPI(title="AI Investment Advisor")

class ChatIn(BaseModel):
    user_id: str
    message: str

class DemographicsIn(BaseModel):
    user_id: str
    demographics: Dict[str, Any]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat_ep(payload: ChatIn):
    reply = chat(payload.user_id, payload.message)
    return {"reply": reply}

@app.post("/calculate_savings")
def calc_savings(payload: DemographicsIn):
    return _tool_savings(payload.user_id, payload.demographics)

@app.post("/recommend_insurance")
def rec_ins(payload: DemographicsIn):
    return _tool_insurance(payload.user_id, payload.demographics)
