import os
from google import genai


class AgentEngine:
    def __init__(self):
        pass

    def process_user_intent(self, prompt: str) -> str:
        api_key = os.environ.get(
            "GEMINI_API_KEY", "").strip().strip('"').strip("'")

        if not api_key:
            return "Error: GEMINI_API_KEY environment variable is missing on Render."

        try:
            # Initialize client with AQ key support
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"Gemini API Error: {str(e)}"
