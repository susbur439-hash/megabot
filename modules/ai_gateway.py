import os
import requests
import time

# =========================================================
# 🔐 CONFIG
# =========================================================

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")

URL = "https://models.github.ai/inference/chat/completions"

# 🚀 SAFE MODELS ONLY (NO PRIVATE / NO LLAMA FAILS)
MODELS = [
    "gpt-4o-mini",
    "gpt-4o"
]


# =========================================================
# 🤖 LOW LEVEL CALL
# =========================================================

def try_model(model, prompt):

    if not GITHUB_TOKEN:
        return None, {"error": "NO_TOKEN"}

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
            timeout=30
        )

        # =========================
        # 🔴 ERROR HANDLING
        # =========================

        if response.status_code in [401, 403]:
            return None, {
                "model": model,
                "error": "ACCESS_DENIED"
            }

        if response.status_code == 429:
            return None, {
                "model": model,
                "error": "RATE_LIMIT"
            }

        if response.status_code != 200:
            return None, {
                "model": model,
                "status": response.status_code,
                "error": response.text[:500]
            }

        try:
            data = response.json()
        except:
            return None, {
                "model": model,
                "error": "INVALID_JSON"
            }

        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        if not text:
            return None, {
                "model": model,
                "error": "EMPTY_RESPONSE",
                "raw": data
            }

        return {
            "text": text,
            "model_used": model
        }, None

    except Exception as e:
        return None, {
            "model": model,
            "error": str(e)
        }


# =========================================================
# 🧠 MAIN ROUTER
# =========================================================

def ask_model(prompt: str):

    if not GITHUB_TOKEN:
        return {
            "error": "MODELS_TOKEN not found"
        }

    last_error = None

    for model in MODELS:

        result, error = try_model(model, prompt)

        if result:
            return result

        last_error = error

        # 🧠 small anti-rate-limit delay
        time.sleep(0.4)

    return {
        "error": "ALL_MODELS_FAILED",
        "last_error": last_error,
        "tried_models": MODELS
    }