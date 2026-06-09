import os
import time
import requests

# =========================================================
# 🧠 MODEL DISCOVERY (DYNAMIC)
# =========================================================

def load_models():
    try:
        from modules.model_discovery import get_models
        models = get_models()
        if models:
            return models
    except:
        pass

    # fallback ONLY SAFE MODELS
    return [
        "openai/gpt-4o-mini",
        "openai/gpt-4o"
    ]


# =========================================================
# 🔧 CONFIG
# =========================================================

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")
URL = "https://models.github.ai/inference/chat/completions"


# =========================================================
# 🤖 LOW-LEVEL CALL
# =========================================================

def try_model(model, prompt):

    if not requests:
        return None, {"error": "NO_REQUESTS"}

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

        # ❌ ACCESS BLOCK
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
# 🧠 ROUTER v3 CORE (MAIN FIX)
# =========================================================

def ask_model(prompt):

    if not GITHUB_TOKEN:
        return {"error": "NO_TOKEN"}

    models = load_models()

    last_error = None
    tried = set()

    for model in models:

        if model in tried:
            continue

        tried.add(model)

        result, error = try_model(model, prompt)

        if result:
            return result

        last_error = error

        # если нет доступа — не повторяем
        if error and error.get("error") == "ACCESS_DENIED":
            continue

        time.sleep(0.3)

    return {
        "error": "ALL_MODELS_FAILED",
        "last_error": last_error,
        "tried_models": list(tried)
    }