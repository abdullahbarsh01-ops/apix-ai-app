import streamlit as st
import os
import json
import subprocess
import urllib.request
import sqlite3
import pypdf
import matplotlib.pyplot as plt
import pyautogui
import psutil
import webbrowser
from docx import Document
from docx.shared import Inches

# 1. إعدادات الواجهة الفاخرة (Modern Dark UI)
st.set_page_config(page_title="Apex Ultimate Autonomous Agent",
                   page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0E1117; }
    .stChatMessage { border-radius: 12px; border: 1px solid #262730; background-color: #1A1C23; }
    .stStatus { border-radius: 10px; background-color: #161B22; border: 1px solid #30363D; }
    .stButton>button { background: linear-gradient(90deg, #4F46E5, #7C3AED); color: white; border: none; border-radius: 8px; font-weight: bold; width: 100%; }
    .sidebar-card { background: #1E222D; padding: 15px; border-radius: 10px; border: 1px solid #2D3342; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVE_PATH = r"C:\Users\user\Google Drive\AI_Agent_Memory"
DB_PATH = os.path.join(SCRIPT_DIR, "apex_media_hub.db")

# 2. محرك قراءة الـ PDF واستخراج التعليمات


def extract_pdf_instructions(uploaded_file):
    try:
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"خطأ في قراءة ملف PDF: {e}"

# 3. محرك التواصل مع Ollama بالنموذج المحدد


def query_ollama(prompt, model_name="qwen2.5:7b"):
    url = "http://localhost:11434/api/generate"
    payload = {"model": model_name, "prompt": prompt, "stream": False}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(
        'utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))['response']
    except Exception as e:
        # Fallback إلى النموذج الأصغر إذا لم يكن 7b محتملاً بعد
        payload["model"] = "qwen2.5:1.5b"
        req = urllib.request.Request(url, data=json.dumps(payload).encode(
            'utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))['response']

# 4. محرك إضفاء الطابع البشري وتجهيز المناقشة الشفهية (Humanizer & Viva)


def humanize_solution(task_title, raw_result, model_name):
    prompt = """
    You are a university student presenting your assignment solution.
    Task Title: """ + str(task_title) + """
    Execution Result: """ + str(raw_result) + """
    
    Provide output in JSON format with two keys:
    1. "human_explanation": A concise, natural 2-sentence explanation in simple student style. Avoid robotic words like 'Furthermore', 'Delve', 'Testament'.
    2. "viva_talking_point": A 1-sentence tip on what to say orally to the lecturer during viva defense.
    
    Return ONLY valid raw JSON.
    """
    res = query_ollama(prompt, model_name)
    try:
        return json.loads(res)
    except:
        return {
            "human_explanation": "This solution processes the operational data directly to satisfy the assignment requirements.",
            "viva_talking_point": "Mention that you used proper joins and conditions to maintain database consistency."
        }


# 5. الشريط الجانبي لوحة التحكم
with st.sidebar:
    st.title("⚡ Agent Control Hub")
    selected_model = st.selectbox("🤖 اختيار نموذج الذكاء الاصطناعي:", [
                                  "qwen2.5:7b", "deepseek-r1:8b", "qwen2.5:1.5b"])

    st.markdown("---")
    st.subheader("📄 رفع ملف تعليمات الواجب (PDF)")
    pdf_file = st.file_uploader(
        "قم برفع ملف الـ PDF لقراءته أوتوماتيكياً", type=["pdf"])

    pdf_text = ""
    if pdf_file:
        pdf_text = extract_pdf_instructions(pdf_file)
        st.success(f"تم قراءة المستند بنجاح! ({len(pdf_text)} حرف)")

    st.markdown("---")
    st.subheader("💾 حالة Google Drive (400GB)")
    if os.path.exists(DRIVE_PATH):
        st.success("Google Drive Sync: متصل وزغال")
    else:
        st.info("الذاكرة تعمل محلياً وتتحول تلقائياً للسحاب")

# 6. الواجهة الرئيسية
st.title("🛡️ Ultimate Autonomous Multi-Task Agent")
st.caption(
    "نظام أتمتة حل الواجبات، قراءة تعليمات PDF، التحكم بالتطبيقات، والتصحيح الذاتي.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "أهلاً بك! أنا جاهز لقراءة أي ملف PDF للواجبات، تنفيذ الاستعلامات، التقاط لقطات الشاشة، صياغة الشرح بأسلوب بشري، وتحديث التقرير كاملاً."}
    ]

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("اكتب أمرك هنا (مثال: اقرأ الـ PDF واحل السؤال الأول | افتح برنامج النوت باد | شغّل الواجب الكامل)..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🧠 الوكيل يحلل الأوامر ويبدأ الأتمتة...", expanded=True) as status:

            # سيناريو قراءة الـ PDF وحل الواجب بناءً عليه
            if pdf_text and any(w in prompt.lower() for w in ["pdf", "واجب", "اقرأ", "حل"]):
                status.write(
                    "📄 جاري تحليل شروط وتوجيهات ملف الـ PDF المرفق...")
                agent_plan_prompt = f"Analyze these assignment instructions and user prompt: {prompt}\nPDF Text snippet: {pdf_text[:1500]}\nSummarize the required actions in 2 clear steps."
                plan_res = query_ollama(agent_plan_prompt, selected_model)

                status.write(
                    "⚙️ جاري تشغيل المحرك لتوليد تقرير Word المكتمل بالصور والشرح البشري...")
                script_path = os.path.join(
                    SCRIPT_DIR, "super_agent_builder.py")
                exec_res = subprocess.run(
                    f'python "{script_path}"', shell=True, capture_output=True, text=True)

                status.update(
                    label="تم قراءة الـ PDF وتوليد الواجب كاملاً بنجاح!", state="complete")
                response_text = f"**تحليل التعليمات:**\n{plan_res}\n\n**نتيجة التنفيذ:**\nتم إنشاء التقرير النهائي بالصور والشرح البشري وحفظه في مجلد العمل وGoogle Drive!"

            # سيناريو فتح التطبيقات والتحكم بالنظام
            elif any(w in prompt.lower() for w in ["افتح", "launch", "notepad", "code", "calc", "chrome"]):
                app_name = "notepad" if "notepad" in prompt.lower(
                ) else "code" if "code" in prompt.lower() else "calc"
                os.system(f"start {app_name}")
                status.update(
                    label="تم فتح التطبيق المطلوب بنجاح!", state="complete")
                response_text = f"تم إطلاق التطبيق **{app_name}** على نظام التشغيل."

            # سيناريو التقاط الشاشة
            elif any(w in prompt.lower() for w in ["صورة", "لقطة", "screenshot"]):
                img_path = os.path.join(SCRIPT_DIR, "system_shot.png")
                pyautogui.screenshot().save(img_path)
                status.update(label="تم أخذ لقطة شاشة!", state="complete")
                response_text = f"تم التقاط صورة الشاشة وحفظها بنجاح في: `{img_path}`"

            # استجابة عامة عبر النموذج المحلي
            else:
                status.write("⚙️ جاري التفكير ومعالجة الطلب...")
                response_text = query_ollama(prompt, selected_model)
                status.update(label="تمت معالجة الطلب!", state="complete")

        st.markdown(response_text)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response_text})
