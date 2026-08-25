import urllib.request
import urllib.parse


class AgentEngine:
    def __init__(self):
        pass

    def process_user_intent(self, prompt: str) -> str:
        try:
            # Encode prompt for clean GET request
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai"

            # Browser-like headers to bypass Cloudflare 403 blocks
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/plain, */*"
                }
            )

            with urllib.request.urlopen(req, timeout=25) as response:
                result = response.read().decode("utf-8")
                return result if result.strip() else "System generated empty response."
        except Exception as e:
            return f"Engine Communication Error: {str(e)}"
