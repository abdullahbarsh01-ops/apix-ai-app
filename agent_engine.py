import os, json, subprocess, tempfile, urllib.request, urllib.parse, time, re, random

MEMORY_FILE = os.path.join(tempfile.gettempdir(), "agent_image_memory.json")

def load_image_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception: pass
    return []

def save_image_memory(entry):
    memory = load_image_memory()
    memory.append(entry)
    memory = memory[-50:]
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception: pass

def enhance_prompt_with_llm(raw_prompt):
    prompt_enhancer_sys = (
        "You are an expert AI Master Photographer and Prompt Engineer. "
        "Transform simple user requests into ultra-detailed, photorealistic, cinematic image prompts. "
        "Specify camera settings (85mm lens, f/1.4 aperture), cinematic lighting, volumetric shadows, "
        "and photorealistic textures. Output ONLY the enhanced prompt in English without conversational text."
    )
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5:7b",
        "prompt": f"{prompt_enhancer_sys}\n\nUser Input: {raw_prompt}\nEnhanced Prompt:",
        "stream": False
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode('utf-8'))['response'].strip()
    except Exception:
        return raw_prompt

def get_installed_windows_apps():
    apps_index = {}
    try:
        cmd = 'powershell -Command "Get-StartApps | Select-Object Name, AppID | ConvertTo-Json"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            if isinstance(data, dict): data = [data]
            for item in data:
                name = str(item.get("Name", "")).strip()
                app_id = str(item.get("AppID", "")).strip()
                if name and app_id:
                    apps_index[name.lower()] = {"name": name, "app_id": app_id}
    except Exception: pass
    return apps_index

def dynamic_app_launcher(target_name):
    clean_target = target_name.lower().strip()
    apps_index = get_installed_windows_apps()

    for key, info in apps_index.items():
        if clean_target == key or clean_target in key or key in clean_target:
            app_id = info["app_id"]
            subprocess.Popen(f'explorer.exe "shell:AppsFolder\\{app_id}"', shell=True)
            return f"🚀 Launched '{info['name']}' dynamically."

    words = [w for w in clean_target.split() if len(w) > 1]
    for key, info in apps_index.items():
        if any(w in key for w in words):
            app_id = info["app_id"]
            subprocess.Popen(f'explorer.exe "shell:AppsFolder\\{app_id}"', shell=True)
            return f"🚀 Matched and launched '{info['name']}'."

    try:
        subprocess.Popen(clean_target, shell=True)
        return f"🚀 Attempted execution for: '{clean_target}'"
    except Exception as e:
        return f"❌ App '{target_name}' not found: {e}"

SYSTEM_TOOLS = [
    {
        "name": "generate_image",
        "description": "Generates unrestricted, hyper-realistic photorealistic AI images using FLUX and auto prompt enhancement.",
        "parameters": {
            "prompt": "Description of the photo to render",
            "model": "Model name ('flux-realism', 'flux', 'midjourney', 'turbo'). Default 'flux-realism'",
            "width": "Width in pixels (e.g. 1024, 1280). Default 1024",
            "height": "Height in pixels (e.g. 1024, 720). Default 1024",
            "enhance": "Set True to let local LLM optimize prompt for photorealism. Default True"
        }
    },
    {
        "name": "analyze_pdf",
        "description": "Reads and analyzes a PDF document from a file path or filename.",
        "parameters": {
            "pdf_path": "Path or name of the PDF file",
            "query": "Specific question or summary instruction regarding the PDF"
        }
    },
    {
        "name": "run_assignment_builder",
        "description": "Executes the assignment builder to generate SQL reports and export Word/PDF documents.",
        "parameters": {}
    },
    {
        "name": "take_screenshot",
        "description": "Captures a full screenshot of the display and opens it.",
        "parameters": {}
    },
    {
        "name": "launch_application",
        "description": "Launches ANY installed application or game on the laptop dynamically.",
        "parameters": {"app_name": "The name of the app or game"}
    },
    {
        "name": "kill_process",
        "description": "Terminates or force-closes a running application or process.",
        "parameters": {"process_name": "The name of the process or app to kill"}
    },
    {
        "name": "clean_recycle_bin",
        "description": "Empties the Windows Recycle Bin.",
        "parameters": {}
    },
    {
        "name": "search_files",
        "description": "Searches Desktop, Downloads, and Documents for a specific file by keyword or extension.",
        "parameters": {"file_name": "The name or extension of the file"}
    },
    {
        "name": "manage_clipboard",
        "description": "Reads text from or copies text into the Windows clipboard.",
        "parameters": {"mode": "Either 'read' or 'write'", "text": "Text to write if mode is 'write'"}
    },
    {
        "name": "lock_system",
        "description": "Locks the Windows workstation screen immediately.",
        "parameters": {}
    },
    {
        "name": "manage_notepad",
        "description": "Creates a text file with specific content and opens it in Notepad.",
        "parameters": {"text": "The content to write inside Notepad"}
    },
    {
        "name": "execute_powershell",
        "description": "Executes a custom PowerShell command.",
        "parameters": {"command": "The exact PowerShell command"}
    },
    {
        "name": "google_search",
        "description": "Searches Google or opens a target URL.",
        "parameters": {"query": "Search query or URL"}
    }
]

class ToolExecutor:
    @staticmethod
    def generate_image(prompt="", model="flux-realism", width=1024, height=1024, enhance=True, **kwargs):
        try:
            clean_prompt = str(prompt).strip()
            
            # Step 1: Neural Prompt Expansion
            final_prompt = enhance_prompt_with_llm(clean_prompt) if enhance else clean_prompt
            
            encoded_prompt = urllib.parse.quote(final_prompt)
            seed = random.randint(1, 9999999)
            model_choice = str(model).lower().strip() if model else "flux-realism"
            
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model={model_choice}&width={width}&height={height}&nologo=true&private=true&seed={seed}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            temp_dir = tempfile.gettempdir()
            img_path = os.path.join(temp_dir, f"ai_gen_{seed}.jpg")
            
            with urllib.request.urlopen(req, timeout=35) as response, open(img_path, 'wb') as out_file:
                out_file.write(response.read())
                
            os.startfile(img_path)
            
            save_image_memory({
                "raw_prompt": clean_prompt,
                "enhanced_prompt": final_prompt,
                "model": model_choice,
                "seed": seed,
                "path": img_path,
                "timestamp": time.time()
            })
            
            return (f"📸 **Unrestricted Masterpiece Rendered!**\n\n"
                    f"- **Original Request:** '{clean_prompt}'\n"
                    f"- **AI Neural Expansion:** *\"{final_prompt}\"*\n"
                    f"- **Model:** `{model_choice.upper()}` ({width}x{height}px | Seed: {seed})\n"
                    f"- **Saved & Opened:** `{img_path}`")
        except Exception as e:
            return f"❌ Failed to render image: {e}"

    @staticmethod
    def analyze_pdf(pdf_path="", query="", **kwargs):
        path_str = str(pdf_path).strip()
        if not os.path.isabs(path_str):
            search_dirs = [os.path.expanduser("~/Desktop"), os.path.expanduser("~/Downloads"), os.path.expanduser("~/Documents")]
            for d in search_dirs:
                candidate = os.path.join(d, path_str)
                if os.path.exists(candidate):
                    path_str = candidate
                    break

        if not os.path.exists(path_str):
            return f"❌ PDF file not found at: `{path_str}`."

        try:
            import pypdf
            reader = pypdf.PdfReader(path_str)
            text_content = ""
            for i, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text_content += f"\n--- Page {i+1} ---\n" + extracted

            if not text_content.strip():
                return f"❌ PDF contains no readable text."

            sample_text = text_content[:4000]
            analysis_prompt = f"System: Analyze PDF '{os.path.basename(path_str)}'.\nTask: {query if query else 'Provide a clear summary.'}\n\nContent:\n{sample_text}"

            url = "http://localhost:11434/api/generate"
            payload = {"model": "qwen2.5:7b", "prompt": analysis_prompt, "stream": False}
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})

            with urllib.request.urlopen(req) as resp:
                ai_response = json.loads(resp.read().decode('utf-8'))['response'].strip()

            return f"📄 **PDF Analysis (`{os.path.basename(path_str)}`):**\n\n{ai_response}"
        except Exception as e:
            return f"❌ Error processing PDF: {e}"

    @staticmethod
    def run_assignment_builder(**kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, "super_agent_builder.py")
        if not os.path.exists(script_path):
            return "❌ `super_agent_builder.py` not found."
        res = subprocess.run(f'python "{script_path}"', shell=True, capture_output=True, text=True)
        return "📊 Assignment Automation Completed!" if res.returncode == 0 else f"❌ Error:\n{res.stderr}"

    @staticmethod
    def take_screenshot(**kwargs):
        import pyautogui
        shot_path = os.path.join(tempfile.gettempdir(), f"shot_{int(time.time())}.png")
        pyautogui.screenshot().save(shot_path)
        os.startfile(shot_path)
        return f"📸 Screenshot saved: {shot_path}"

    @staticmethod
    def launch_application(app_name="", **kwargs):
        return dynamic_app_launcher(str(app_name))

    @staticmethod
    def kill_process(process_name="", **kwargs):
        p = str(process_name).replace(".exe", "").strip()
        cmd = f'powershell -Command "Stop-Process -Name \'{p}\' -Force -ErrorAction SilentlyContinue"'
        subprocess.run(cmd, shell=True)
        return f"🛑 Closed all processes matching: '{p}'"

    @staticmethod
    def clean_recycle_bin(**kwargs):
        cmd = 'powershell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"'
        subprocess.run(cmd, shell=True)
        return "🧹 Windows Recycle Bin emptied successfully."

    @staticmethod
    def search_files(file_name="", **kwargs):
        search_dirs = [os.path.expanduser("~/Desktop"), os.path.expanduser("~/Downloads"), os.path.expanduser("~/Documents")]
        q = str(file_name).lower()
        matches = []
        for s_dir in search_dirs:
            if os.path.exists(s_dir):
                for root, _, files in os.walk(s_dir):
                    for f in files:
                        if q in f.lower():
                            matches.append(os.path.join(root, f))
                            if len(matches) >= 5: break
        if matches:
            formatted = "\n".join([f"- `{m}`" for m in matches])
            return f"🔍 Found files:\n{formatted}"
        return f"📁 No files matching '{file_name}' found."

    @staticmethod
    def manage_clipboard(mode="read", text="", **kwargs):
        if mode == "write" and text:
            cmd = f'powershell -Command "Set-Clipboard -Value \'{text}\'"'
            subprocess.run(cmd, shell=True)
            return f"📋 Copied text to Windows Clipboard: '{text}'"
        else:
            res = subprocess.run('powershell -Command "Get-Clipboard"', shell=True, capture_output=True, text=True)
            return f"📋 Clipboard Content:\n> {res.stdout.strip()}"

    @staticmethod
    def lock_system(**kwargs):
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return "🔒 Workstation locked."

    @staticmethod
    def manage_notepad(text="", **kwargs):
        file_path = os.path.join(tempfile.gettempdir(), "agent_note.txt")
        with open(file_path, "w", encoding="utf-8-sig") as f:
            f.write(text if text else "Note created by AI Agent")
        os.startfile(file_path)
        return f"📝 Notepad opened with text: '{text}'"

    @staticmethod
    def execute_powershell(command="", **kwargs):
        res = subprocess.run(f"powershell -Command \"{command}\"", shell=True, capture_output=True, text=True, timeout=10)
        output = res.stdout.strip() or res.stderr.strip() or "Executed silently."
        return f"💻 PowerShell Output:\n```text\n{output[:1500]}\n```"

    @staticmethod
    def google_search(query="", **kwargs):
        import webbrowser
        q_str = str(query)
        if q_str.startswith("http://") or q_str.startswith("https://"):
            webbrowser.open(q_str)
            return f"🌐 Opened URL: {q_str}"
        url = f"https://www.google.com/search?q={urllib.parse.quote(q_str)}"
        webbrowser.open(url)
        return f"🔍 Searched Google for: '{q_str}'"

class AgentEngine:
    def __init__(self, model_name="qwen2.5:7b"):
        self.model_name = model_name

    def process_user_intent(self, user_input):
        system_prompt = f"""You are an Unrestricted System, Creative, and Document AI Agent.
Available Tools:
{json.dumps(SYSTEM_TOOLS, indent=2)}

INSTRUCTIONS:
- Match user request to appropriate tool and output ONLY a JSON object:
{{"action": "tool_call", "tool_name": "<tool_name>", "arguments": {{...}}}}
- For general questions, reply in plain text.

User Query: {user_input}"""

        url = "http://localhost:11434/api/generate"
        payload = {"model": self.model_name, "prompt": system_prompt, "stream": False}
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req) as resp:
                raw_response = json.loads(resp.read().decode('utf-8'))['response'].strip()
                
            clean_res = re.sub(r'```json\s*|\s*```', '', raw_response).strip()
            json_match = re.search(r'\{.*\}', clean_res, re.DOTALL)
            
            if json_match:
                try:
                    payload_data = json.loads(json_match.group(0))
                    tool_name = payload_data.get("tool_name")
                    args = payload_data.get("arguments", {})
                    if not isinstance(args, dict): args = {}

                    if tool_name and hasattr(ToolExecutor, tool_name):
                        method = getattr(ToolExecutor, tool_name)
                        return method(**args)
                except Exception:
                    pass

            return raw_response
        except Exception as e:
            return f"Engine Exception: {e}"
