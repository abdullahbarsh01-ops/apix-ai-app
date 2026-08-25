import urllib.request
import urllib.parse


class AgentEngine:
    def __init__(self):
        # 1st: Meta Llama 3.3 70B (Most Powerful Open Model)
        # 2nd: Qwen 2.5 (Top Reasoning & Coding Model)
        # 3rd: Mistral (Fast Fallback)
        self.models = ["llama", "qwen-coder", "mistral"]

    def process_user_intent(self, prompt: str) -> str:
        encoded_prompt = urllib.parse.quote(prompt)

        for model in self.models:
            try:
                url = f"https://text.pollinations.ai/{encoded_prompt}?model={model}"
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/plain, */*"
                    }
                )

                with urllib.request.urlopen(req, timeout=15) as response:
                    result = response.read().decode("utf-8")
                    if result.strip():
                        return result.strip()
            except Exception:
                continue  # Instantly route to next backup model if busy

        return "Quantum Core Busy: Please resend your query."
