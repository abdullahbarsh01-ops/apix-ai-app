import urllib.request
import urllib.parse


class AgentEngine:
    def __init__(self):
        # Fast, stable models
        self.models = ["mistral", "llama", "openai-fast"]

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
        # Direct prompt combination for fast processing
        full_text = f"{self.system_prompt}\n\nرسالة حبيبة عبدالله: {prompt}\n\nالإجابة الرومانسية:"
        encoded_prompt = urllib.parse.quote(full_text)

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

                # 25s timeout gives free servers enough time to process full Arabic text
                with urllib.request.urlopen(req, timeout=25) as response:
                    result = response.read().decode("utf-8")
                    if result.strip() and "Error" not in result:
                        return result.strip()
            except Exception:
                continue

        return "عبدالله يحبكِ جداً وينتظر أن يسمع منكِ دائماً! أرسلي لي رسالة أخرى يا أميرتي."
