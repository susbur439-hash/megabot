import os
import requests

# =========================================================
# 🔐 TOKEN
# =========================================================

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")

# =========================================================
# 🤖 AVAILABLE MODELS (fallback list)
# =========================================================

MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini",
    "gpt-3.5-turbo"
]

URL = "https://models.github.ai/inference/chat/completions"


# =========================================================
# 🧠 AUTO MODEL SELECT
# =========================================================

def try_model(model, prompt):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(
            URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        # если модель не поддерживается — пробуем следующую
        if response.status_code != 200:
            return None, {
                "error": response.text,
                "status": response.status_code,
                "model": model
            }

        data = response.json()

        content = None
        try:
            content = data["choices"][0]["message"]["content"]
        except:
            content = str(data)

        return {
            "raw": data,
            "text": content,
            "model_used": model
        }, None

    except Exception as e:
        return None, {
            "error": str(e),
            "model": model
        }


# =========================================================
# 🚀 MAIN FUNCTION (AUTO FALLBACK)
# =========================================================

def ask_model(prompt: str):
    """
    Авто-выбор рабочей модели GitHub Models
    """

    if not GITHUB_TOKEN:
        return {"error": "MODELS_TOKEN not found"}

    last_error = None

    for model in MODELS:
        result, error = try_model(model, prompt)

        if result:
            return result

        last_error = error

    return {
        "error": "All models failed",
        "last_error": last_error
    }