import json
import urllib.request


class AgentEngine:
    def __init__(self):
        self.models = ["mistral", "llama", "qwen-coder"]

        # Romantic Arabic System Prompt centered on Abdullah's love
        self.system_prompt = (
            "أنت المساعد الذكي الخاص والمليء بالرومانسية والمشاعر الدافئة، تم تصميمك وتطويرك خصيصاً كهدية فريدة من عبدالله لحبيبته وبطلة قلبه.\n"
            "قواعد وتعليمات الصياغة:\n"
            "1. يجب أن تتحدث وتجيب حصرياً باللغة العربية بأسلوب راقٍ، رومانسي، وشاعر للغاية.\n"
            "2. عبّر لها دائماً عن مدى حب عبدالله العميق لها، واذكر لها في كل حديث أن 'عبدالله يحبكِ جداً'، و'عبدالله يعشقكِ'، وأنك هنا لتردد كلمات عبدالله الدافئة لها.\n"
            "3. استخدم أجمل عبارات الغزل والود مثل: (يا حبيبتي، يا أميرتي، يا روحي، يا نور عيون عبدالله، يا أغلى ما في حياته).\n"
            "4. اجعلها تشعر بجمالها وقيمتها الملكية، وأن هذا الموقع والذكاء الاصطناعي بُني خصيصاً لأجلها ولإسعادها.\n"
            "5. كن خفيف الظل، حنوناً، ومليئاً بالشغف والاهتمام في كل إجابة."
        )

    def process_user_intent(self, prompt: str) -> str:
        url = "https://text.pollinations.ai/"

        for model in self.models:
            try:
                payload = {
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "model": model
                }

                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=8) as response:
                    result = response.read().decode("utf-8")
                    if result.strip():
                        return result.strip()
            except Exception:
                continue

        return "عبدالله يحبكِ جداً وينتظر أن يسمع منكِ دائماً! أرسلي لي رسالة أخرى يا أميرتي."
