import json
import urllib.request


class AgentEngine:
    def __init__(self):
        pass

    def process_user_intent(self, prompt: str) -> str:
        url = "https://text.pollinations.ai/"

        payload = {
            "messages": [
                {"role": "system", "content": "You are APEX AI, a helpful, futuristic, and highly intelligent AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "model": "openai"
        }

        headers = {"Content-Type": "application/json"}

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8")
        except Exception as e:
            return f"AI Service Error: {str(e)}"
