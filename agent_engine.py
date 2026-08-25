import os
import json
import urllib.request


class AgentEngine:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")

    def process_user_intent(self, prompt: str):
        if not self.api_key:
            return "Error: GEMINI_API_KEY environment variable is not set on Render."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Gemini API Error: {str(e)}"
