import os
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agent_engine import AgentEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = AgentEngine()


class ChatRequest(BaseModel):
    prompt: Optional[str] = None
    message: Optional[str] = None
    text: Optional[str] = None


@app.get("/")
def read_root():
    return {"status": "APEX AI Cloud Engine is Live!"}


@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        user_input = body.get("prompt") or body.get(
            "message") or body.get("text") or ""

        if not user_input:
            return {"response": "Error: Empty prompt received by server."}

        reply = agent.process_user_intent(user_input)
        return {"response": reply}
    except Exception as e:
        return {"response": f"Server Exception: {str(e)}"}
