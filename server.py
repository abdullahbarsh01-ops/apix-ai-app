import os
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    query: Optional[str] = None


@app.get("/")
def read_root():
    return {"status": "APEX AI Cloud Engine is Live!"}


@app.post("/chat")
def chat(request: ChatRequest):
    # Extract prompt regardless of key name used by frontend JS
    user_input = request.prompt or request.message or request.text or request.query or ""
    if not user_input:
        return {"response": "Error: Empty prompt received."}

    reply = agent.process_user_intent(user_input)
    return {"response": reply}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
