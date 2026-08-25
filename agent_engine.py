import json
import urllib.request
import urllib.parse


class AgentEngine:
    def __init__(self):
        pass

    def process_user_intent(self, prompt: str) -> str:
        try:
            url = "https://text.pollinations.ai/"

            payload = {
                "messages": [
                    {"role": "system", "content": "You are APEX AI, a highly intelligent, helpful, and futuristic AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                "model": "openai"
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=25) as response:
                result = response.read().decode("utf-8")
                return result if result.strip() else "System generated empty response."
        except Exception as e:
            return f"Engine Communication Error: {str(e)}"
