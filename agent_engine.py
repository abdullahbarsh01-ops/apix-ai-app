import os
import google.generativeai as genai


class AgentEngine:
    def __init__(self):
        pass

    def process_user_intent(self, prompt: str):
        # Fetch key and strip whitespace/quotes
        raw_key = os.environ.get("GEMINI_API_KEY", "").strip()
        api_key = raw_key.strip('"').strip("'").strip()

        if not api_key:
            return "Error: GEMINI_API_KEY environment variable is missing on Render."

        # Mask key for debug logs (shows first 4 and last 4 characters)
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(
            api_key) > 8 else "SHORT_KEY"
        print(
            f"DEBUG LOG: Attempting Gemini call with Key: {masked_key} (Length: {len(api_key)})")

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error (Loaded Key: {masked_key}): {str(e)}"
