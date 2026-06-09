import os
import json
import requests

TOKEN = os.getenv("MODELS_TOKEN")

OUTPUT_FILE = "working_models.json"

# список кандидатов можно расширять
CANDIDATES = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4.1",
    "gpt-4.1-mini",
    "o4-mini",
    "o3",
    "phi-4",
    "mistral-small",
    "mistral-medium",
    "llama-3.3-70b-instruct",
    "llama-3.1-70b-instruct",
    "deepseek-r1"
]

URL = "https://models.github.ai/inference/chat/completions"


def test_model(model):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "hello"}
        ],
        "max_tokens": 5
    }

    try:
        r = requests.post(
            URL,
            json=payload,
            headers=headers,
            timeout=20
        )

        return r.status_code == 200

    except Exception:
        return False


def discover_models():

    if not TOKEN:
        print("MODELS_TOKEN not found")
        return []

    working = []

    print("=== MODEL DISCOVERY ===")

    for model in CANDIDATES:

        print(f"Testing: {model}")

        if test_model(model):
            print(f"OK: {model}")
            working.append(model)
        else:
            print(f"FAIL: {model}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            working,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("WORKING MODELS:")
    print(working)

    return working


if __name__ == "__main__":
    discover_models()