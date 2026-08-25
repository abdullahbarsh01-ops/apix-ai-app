import os
import google.generativeai as genai


class AgentEngine:
    def __init__(self):
        pass

    def process_user_intent(self, prompt: str) -> str:
        # Extract and clean key string
        raw_key = os.environ.get("GEMINI_API_KEY", "").strip()
        api_key = raw_key.strip('"').strip("'").strip()

        if not api_key:
            return "Error: GEMINI_API_KEY environment variable is missing on Render."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini API Error: {str(e)}"
