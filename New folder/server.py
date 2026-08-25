from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_engine import AgentEngine

app = FastAPI(title="APEX AI Web API")

# Enable CORS for web frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = AgentEngine()


class UserPrompt(BaseModel):
    message: str


@app.post("/api/chat")
async def chat_endpoint(payload: UserPrompt):
    try:
        response = engine.process_user_intent(payload.message)
        if isinstance(response, dict) and response.get("type") == "image":
            import base64
            img_b64 = base64.b64encode(response["image_bytes"]).decode('utf-8')
            return {"type": "image", "image_b64": img_b64, "prompt": response["raw_prompt"]}
        return {"type": "text", "response": str(response)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
