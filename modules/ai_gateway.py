import os
import requests

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")

URL = "https://models.github.ai/inference/chat/completions"

MODEL = "gpt-4o-mini"


def ask_model(prompt: str):

    if not GITHUB_TOKEN:
        return {
            "error": "MODELS_TOKEN not found"
        }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
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

        result = {
            "status_code": response.status_code,
            "response_text": response.text[:3000]
        }

        if response.status_code != 200:
            return {
                "error": "request_failed",
                "debug": result
            }

        try:
            data = response.json()
        except Exception as e:
            return {
                "error": f"json_error: {e}",
                "debug": result
            }

        return data

    except Exception as e:
        return {
            "error": str(e)
        }