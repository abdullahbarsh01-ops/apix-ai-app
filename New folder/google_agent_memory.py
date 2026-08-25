import os
import json
import subprocess
import urllib.request

# 1. مسار مجلد Google Drive السحابي (تأكد من تعديل المسار حسب جهازك)
# أو G:\My Drive\AI_Agent_Memory
GOOGLE_DRIVE_FOLDER = r"C:\Users\user\Google Drive\AI_Agent_Memory"
os.makedirs(GOOGLE_DRIVE_FOLDER, exist_ok=True)

MEMORY_FILE = os.path.join(GOOGLE_DRIVE_FOLDER, "agent_cloud_memory.json")

# 2. قراءة الذاكرة من Google Storage


def load_google_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"successful_tasks": [], "learned_fixes": []}

# 3. حفظ الذاكرة والتصحيح الذاتي سحابياً


def save_google_memory(task, code, result, success=True, error_msg=""):
    memory = load_google_memory()
    entry = {
        "task": task,
        "code": code,
        "result": str(result),
        "error_msg": str(error_msg),
        "success": success
    }
    if success:
        memory["successful_tasks"].append(entry)
    else:
        memory["learned_fixes"].append(entry)

    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=4, ensure_ascii=False)
    print(f" تم التحديث والحفظ في Google Storage (400GB): {MEMORY_FILE}")

# 4. محرك التصحيح الذاتي التلقائي عبر النموذج المحلي


def ask_llm(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(
        'utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))['response']


def execute_and_correct(task_description, code_to_run):
    print(f"\n--- جاري تنفيذ المهمة: {task_description} ---")
    temp_file = "temp_exec.py"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(code_to_run)

    res = subprocess.run(f"python {temp_file}",
                         shell=True, capture_output=True, text=True)

    if res.returncode == 0:
        print(" تم التنفيذ بنجاح!")
        save_google_memory(task_description, code_to_run,
                           res.stdout, success=True)
        return True
    else:
        print(" حدث خطأ، جاري التصحيح الذاتي والتخزين في Google Drive...")
        prompt = f"Fix this Python code. Task: {task_description}\nCode:\n{code_to_run}\nError:\n{res.stderr}\nReturn ONLY pure valid Python code."
        fixed_code = ask_llm(prompt).replace(
            "```python", "").replace("```", "").strip()

        save_google_memory(task_description, code_to_run,
                           res.stderr, success=False, error_msg=res.stderr)

        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        res_retry = subprocess.run(
            f"python {temp_file}", shell=True, capture_output=True, text=True)
        if res_retry.returncode == 0:
            print(" تم تصحيح الكود بنجاح في المحاولة الثانية!")
            save_google_memory(task_description, fixed_code,
                               res_retry.stdout, success=True)
            return True
    return False


if __name__ == "__main__":
    test_code = "print('Testing Google Drive Memory Integration'); import docx; d = docx.Document(); d.save('test_drive.docx')"
    execute_and_correct("Test Google Cloud Memory", test_code)
