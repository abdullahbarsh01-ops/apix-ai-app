import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/")
def read_root():
    return {"status": "APEX AI Cloud Engine is Live!"}


@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        user_input = body.get("prompt") or body.get(
            "message") or body.get("text") or body.get("query") or ""

        if not user_input.strip():
            return {"response": "Error: Empty query received."}

        reply = agent.process_user_intent(user_input)
        return {"response": reply}
    except Exception as e:
        return {"response": f"Server Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
