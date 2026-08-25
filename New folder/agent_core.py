import urllib.request
import json


def ask_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5:1.5b",
        "prompt": prompt,
        "stream": False
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['response']
    except Exception as e:
        return f"خطأ في الاتصال: {e}"


if __name__ == "__main__":
    print("جاري إرسال طلب تجريبي للنموذج المحلي...")
    test_prompt = "Write a simple SQL CREATE TABLE statement for a 'Members' table with id, name, and fine_amount."
    response = ask_ollama(test_prompt)

    print("\n--- استجابة النموذج ---")
    print(response)
