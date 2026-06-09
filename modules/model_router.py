import os
import time
import requests

# =========================================================
# 🧠 SAFE MODEL ROUTER v3 FIXED
# =========================================================

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")
URL = "https://models.github.ai/inference/chat/completions"

# 🚀 ONLY CONFIRMED WORKING PATTERN MODELS
BASE_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini",
    "o3-mini",
    "o4-mini"
]


# =========================================================
# 🤖 LOW LEVEL CALL
# =========================================================

def try_model(model, prompt):

    if not requests:
        return None, {"error": "NO_REQUESTS"}

    if not GITHUB_TOKEN:
        return None, {"error": "NO_TOKEN"}

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        r = requests.post(URL, json=payload, headers=headers, timeout=30)

        # ❌ ACCESS FIX
        if r.status_code in [401, 403]:
            return None, {"error": "ACCESS_DENIED", "model": model}

        if r.status_code == 429:
            return None, {"error": "RATE_LIMIT", "model": model}

        if r.status_code != 200:
            return None, {"error": r.text, "model": model}

        data = r.json()

        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        return {
            "text": text,
            "model": model,
            "raw": data
        }, None

    except Exception as e:
        return None, {"error": str(e), "model": model}


# =========================================================
# 🧠 ROUTER CORE FIXED
# =========================================================

def ask_model(prompt):

    if not GITHUB_TOKEN:
        return {"error": "NO_TOKEN"}

    last_error = None
    tried_models = []

    for model in BASE_MODELS:

        tried_models.append(model)

        result, error = try_model(model, prompt)

        if result and result.get("text"):
            return {
                "text": result["text"],
                "model_used": model
            }

        last_error = error

        # ⛔ anti-rate-limit safe delay
        time.sleep(0.4)

    return {
        "error": "ALL_MODELS_FAILED",
        "last_error": last_error,
        "tried_models": tried_models
    }