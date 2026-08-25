import streamlit as st
import os, subprocess, tempfile, json, urllib.request, urllib.parse, re, webbrowser, time

st.set_page_config(page_title="Apex Ultra Agent", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0E1117; }
    .stChatMessage { border-radius: 12px; border: 1px solid #262730; background-color: #1A1C23; }
    .stButton>button { background: linear-gradient(90deg, #4F46E5, #7C3AED); color: white; border: none; border-radius: 8px; font-weight: bold; width: 100%; }
</style>
""", unsafe_allow_html=True)

def tool_notepad(text):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, "agent_note.txt")
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write(text if text else "ملاحظة جديدة")
    os.startfile(file_path)
    return f"📝 تم فتح المفكرة وتدوين النص المباشر:\n\n> **{text}**"

def tool_calc(expr=""):
    subprocess.Popen("calc.exe")
    if expr:
        try:
            res = eval(expr.replace("x", "*").replace("X", "*"))
            return f"🔢 تم فتح الحاسبة والنتيجة: `{expr} = {res}`"
        except: pass
    return "🔢 تم فتح تطبيق الحاسبة."

def tool_screenshot():
    try:
        import pyautogui
        temp_dir = tempfile.gettempdir()
        shot_path = os.path.join(temp_dir, f"screenshot_{int(time.time())}.png")
        pyautogui.screenshot().save(shot_path)
        os.startfile(shot_path)
        return f"📸 تم التقاط لقطة الشاشة وحفظها وفتحها فوراً:\n`{shot_path}`"
    except Exception as e:
        return f"خطأ أثناء التقاط الشاشة: {e}"

def tool_web(query):
    if query.startswith("http://") or query.startswith("https://"):
        webbrowser.open(query)
        return f"🌐 تم فتح الرابط: {query}"
    else:
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"🔍 تم البحث في Google عن: **{query}**"

def query_llm(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {"model": "qwen2.5:7b", "prompt": prompt, "stream": False}
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))['response']
    except Exception:
        return f"🤖 مرحباً بك! أنا الوكيل الذكي، تلقيت استفسارك: \"{prompt}\"."

st.title("🛡️ Apex Ultra Autonomous Agent")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "أهلاً بك! أنا جاهز تماماً لتنفيذ الأوامر (لقطات الشاشة، المفكرة، البحث في Google، والتحدث المباشر)."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("اكتب أمرك هنا (مثال: take a screenshot | hello | افتح النوت باد)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        p_lower = prompt.lower().strip()
        
        if any(w in p_lower for w in ["screenshot", "shot", "لقطة", "شاشة", "شاشه"]):
            res = tool_screenshot()
        elif any(w in p_lower for w in ["notepad", "notebad", "نوت باد", "المفكرة", "مفكرة"]):
            match = re.search(r'(?:اكتب|سجل|write|type)\s+(.+)', prompt, re.IGNORECASE)
            text = match.group(1).strip() if match else "مساء الخير"
            res = tool_notepad(text)
        elif any(w in p_lower for w in ["calc", "حاسبة", "احسب"]):
            m = re.search(r'(\d+[\s\*\+\-\/xX]+\d+)', prompt)
            res = tool_calc(m.group(1) if m else "")
        elif any(w in p_lower for w in ["search", "google", "ابحث", "بحث"]):
            q = re.sub(r'^(search for|search|google|ابحث عن|ابحث|بحث)\s+', '', prompt, flags=re.IGNORECASE).strip()
            res = tool_web(q)
        else:
            res = query_llm(prompt)

        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})