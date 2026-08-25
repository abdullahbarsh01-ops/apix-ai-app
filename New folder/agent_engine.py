import os
import json
import subprocess
import tempfile
import urllib.request
import urllib.parse
import time
import re
import random
import webbrowser
import psutil

# ==========================================
# 🛑 GEMINI API KEY CONFIGURATION
# ==========================================
# Replace hardcoded key string with environment variable lookup
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# ==========================================

CONVERSATION_HISTORY = []


def query_llm(messages_list):
    contents = [{"role": msg["role"], "parts": [{"text": msg["text"]}]}
                for msg in messages_list]
    safety_settings = [
        {"category": f"HARM_CATEGORY_{cat}", "threshold": "BLOCK_NONE"}
        for cat in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT", "CIVIC_INTEGRITY"]
    ]
    payload = {"contents": contents, "safetySettings": safety_settings}
    data = json.dumps(payload).encode('utf-8')

    endpoints = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-001:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    ]
    headers = {'Content-Type': 'application/json',
               'x-goog-api-key': GEMINI_API_KEY}

    for ep in endpoints:
        url = f"{ep}?key={GEMINI_API_KEY}"
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                candidate = res['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    return candidate['content']['parts'][0]['text'].strip()
        except Exception:
            continue

    try:
        flat_prompt = "\n".join(
            [f"{m['role']}: {m['text']}" for m in messages_list])
        ollama_url = "http://localhost:11434/api/generate"
        ollama_payload = {"model": "qwen2.5:7b",
                          "prompt": flat_prompt, "stream": False}
        req = urllib.request.Request(ollama_url, data=json.dumps(
            ollama_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode('utf-8'))['response'].strip()
    except Exception as e:
        return f"❌ AI Engine Error: {e}"


def extract_text_from_url(url_address):
    try:
        req = urllib.request.Request(
            url_address, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            text = re.sub(r'<script.*?>.*?</script>',
                          '', html, flags=re.DOTALL)
            text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<.*?>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3500]
    except Exception as e:
        return f"Could not extract web content: {e}"


SYSTEM_TOOLS = [
    {
        "name": "ai_web_researcher",
        "description": "ONLY use when asked to read, summarize, or research a specific website or URL link.",
        "parameters": {"url": "The full website URL to read and summarize", "topic": "What to focus the summary on"}
    },
    {
        "name": "ai_code_studio",
        "description": "ONLY use when the user explicitly asks to write, generate, or debug code/scripts.",
        "parameters": {"language": "Programming language", "task": "Description of the code to generate"}
    },
    {
        "name": "generate_image_premium",
        "description": "ONLY use when the user explicitly asks to create, draw, or generate an image or artwork.",
        "parameters": {
            "prompt": "Full detailed visual prompt",
            "style": "Optional style preset (e.g. 'photorealistic', 'cyberpunk', 'anime', 'cinematic')"
        }
    },
    {
        "name": "open_website",
        "description": "ONLY use when asked to open a specific website tab (e.g., YouTube, Google).",
        "parameters": {"url_or_site": "The site name or URL to open"}
    },
    {
        "name": "get_system_telemetry",
        "description": "Checks live CPU, RAM, and Disk metrics.",
        "parameters": {}
    },
    {
        "name": "launch_application",
        "description": "Launches desktop software or apps.",
        "parameters": {"app_name": "Name of desktop app to launch"}
    },
    {
        "name": "take_screenshot",
        "description": "Captures a full desktop screenshot.",
        "parameters": {}
    }
]


class ToolExecutor:
    @staticmethod
    def ai_web_researcher(url="", topic="", **kwargs):
        target_url = url.strip()
        if not target_url.startswith("http"):
            target_url = "https://" + target_url
        raw_text = extract_text_from_url(target_url)
        if raw_text.startswith("Could not"):
            return f"❌ {raw_text}"

        prompt = f"Summarize the following web content accurately focusing on '{topic if topic else 'main points'}':\n\n{raw_text}"
        summary = query_llm([{"role": "user", "text": prompt}])
        return f"🌐 **AI Web Synthesis (`{target_url}`):**\n\n{summary}"

    @staticmethod
    def ai_code_studio(language="python", task="", **kwargs):
        prompt = (
            f"Write clean, production-ready code in {language}.\n"
            f"Task: {task}\n"
            "Provide ONLY the code block and brief explanation."
        )
        code_result = query_llm([{"role": "user", "text": prompt}])
        return f"💻 **AI Code Studio ({language.upper()}):**\n\n{code_result}"

    @staticmethod
    def generate_image_premium(prompt="", style="photorealistic", **kwargs):
        try:
            clean_input = str(prompt).strip()
            styled_prompt = f"{clean_input}, {style} style, ultra high resolution, highly detailed"
            encoded_prompt = urllib.parse.quote(styled_prompt)
            seed = random.randint(1, 9999999)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&width=1024&height=1024&nologo=true&seed={seed}"
            req = urllib.request.Request(
                url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=40) as response:
                image_bytes = response.read()
            return {
                "type": "image",
                "image_bytes": image_bytes,
                "raw_prompt": clean_input,
                "enhanced_prompt": styled_prompt
            }
        except Exception as e:
            return f"❌ Image generation error: {e}"

    @staticmethod
    def open_website(url_or_site="", **kwargs):
        target = str(url_or_site).strip().lower()
        target_url = "https://www.youtube.com" if "youtube" in target else (
            "https://www.google.com" if "google" in target else (target if target.startswith("http") else f"https://www.{target}.com"))
        webbrowser.open_new_tab(target_url)
        return f"🌐 Opened '{target_url}' in browser."

    @staticmethod
    def get_system_telemetry(**kwargs):
        cpu = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory()
        return f"📊 **System Telemetry:** CPU `{cpu}%` | RAM `{ram.percent}%`"

    @staticmethod
    def launch_application(app_name="", **kwargs):
        subprocess.Popen(str(app_name), shell=True)
        return f"🚀 Launched '{app_name}'."

    @staticmethod
    def take_screenshot(**kwargs):
        import pyautogui
        shot_path = os.path.join(
            tempfile.gettempdir(), f"shot_{int(time.time())}.png")
        pyautogui.screenshot().save(shot_path)
        os.startfile(shot_path)
        return f"📸 Screenshot captured: `{shot_path}`"


class AgentEngine:
    def process_user_intent(self, user_input):
        global CONVERSATION_HISTORY

        CONVERSATION_HISTORY.append({"role": "user", "text": user_input})
        if len(CONVERSATION_HISTORY) > 10:
            CONVERSATION_HISTORY = CONVERSATION_HISTORY[-10:]

        system_instruction = (
            "You are APEX AI, a High-Level AI Task & Creative Engine.\n"
            "STRICT CHAT RULE: For casual greetings (e.g. 'hi', 'hello', 'hey', 'how are you'), general questions, or normal conversations, respond ONLY with plain conversational text. DO NOT call any tool.\n"
            "STRICT TOOL RULE: ONLY call a tool when the user explicitly requests code, image generation, web research, or system actions. When calling a tool, respond ONLY with a JSON object in this exact format:\n"
            '{"action": "tool_call", "tool_name": "<tool_name>", "arguments": { ... }}\n'
            f"Available Tools:\n{json.dumps(SYSTEM_TOOLS, indent=2)}"
        )

        full_payload_messages = [
            {"role": "user", "text": system_instruction}] + CONVERSATION_HISTORY
        raw_response = query_llm(full_payload_messages)

        clean_res = re.sub(r'```json\s*|\s*```', '', raw_response).strip()
        json_match = re.search(r'\{.*\}', clean_res, re.DOTALL)

        if json_match:
            try:
                payload_data = json.loads(json_match.group(0))
                tool_name = payload_data.get("tool_name")
                args = payload_data.get("arguments", {})
                if not isinstance(args, dict):
                    args = {}

                if tool_name and hasattr(ToolExecutor, tool_name):
                    res = getattr(ToolExecutor, tool_name)(**args)
                    if isinstance(res, dict) and res.get("type") == "image":
                        CONVERSATION_HISTORY.append(
                            {"role": "model", "text": f"Rendered image: '{res['raw_prompt']}'"})
                    else:
                        CONVERSATION_HISTORY.append(
                            {"role": "model", "text": str(res)})
                    return res
            except Exception:
                pass

        CONVERSATION_HISTORY.append({"role": "model", "text": raw_response})
        return raw_response
