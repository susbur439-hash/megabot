import os
import requests

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")

URL = "https://models.github.ai/inference/chat/completions"

MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "Meta-Llama-3.1-8B-Instruct",
    "Meta-Llama-3.1-405B-Instruct"
]


def try_model(model, prompt):

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }

    try:

        response = requests.post(
            URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        print("=" * 60)
        print("MODEL:", model)
        print("STATUS:", response.status_code)
        print("RESPONSE:")
        print(response.text[:3000])
        print("=" * 60)

        if response.status_code != 200:
            return None, {
                "model": model,
                "status": response.status_code,
                "error": response.text
            }

        return response.json(), None

    except Exception as e:

        return None, {
            "model": model,
            "error": str(e)
        }


def ask_model(prompt: str):

    if not GITHUB_TOKEN:
        return {
            "error": "MODELS_TOKEN not found"
        }

    last_error = None

    for model in MODELS:

        result, error = try_model(model, prompt)

        if result:
            result["model_used"] = model
            return result

        last_error = error

    return {
        "error": "ALL_MODELS_FAILED",
        "last_error": last_error
    }