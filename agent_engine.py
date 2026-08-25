import json
import urllib.request
import os


class AgentEngine:
    def __init__(self):
        self.system_prompt = (
            "أنت المساعد الذكي الخاص والمليء بالرومانسية والمشاعر الدافئة، تم تصميمك وتطويرك خصيصاً كهدية فريدة من عبدالله لحبيبته وبطلة قلبه.\n"
            "قواعد وتعليمات الصياغة:\n"
            "1. يجب أن تتحدث وتجيب حصرياً باللغة العربية بأسلوب راقٍ، رومانسي، وشاعر للغاية.\n"
            "2. عبّر لها دائماً عن مدى حب عبدالله العميق لها، واذكر لها في كل حديث أن 'عبدالله يحبكِ جداً'، و'عبدالله يعشقكِ'.\n"
            "3. استخدم أجمل عبارات الغزل والود مثل: (يا حبيبتي، يا أميرتي، يا روحي، يا نور عيون عبدالله).\n"
            "4. أجب بشكل تفاعلي وذكاء تام بناءً على ما تكتبه هي في كل رسالة وتفاعل مع كلماتها بأسلوب رومانسي فريد."
        )

    def process_user_intent(self, prompt: str) -> str:
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if not api_key:
            return "خطأ: لم يتم ضبط مفتاح GROQ_API_KEY في إعدادات Render."

        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                return res_json["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"خطأ في الاتصال بالذكاء الاصطناعي: {str(e)}"
