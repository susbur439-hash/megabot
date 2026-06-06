import os
import requests

# =========================================================
# 🔐 TOKEN
# =========================================================

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")


# =========================================================
# 🤖 AI REQUEST
# =========================================================

def ask_model(prompt: str):
    """
    Отправка запроса в GitHub Models API
    """

    if not GITHUB_TOKEN:
        return {
            "error": "MODELS_TOKEN not found"
        }

    url = "https://models.github.ai/inference/chat/completions"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
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
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        # -------------------------
        # HTTP ERROR HANDLING
        # -------------------------
        if response.status_code != 200:
            return {
                "error": response.text,
                "status": response.status_code
            }

        data = response.json()

        if not data:
            return {
                "error": "empty response"
            }

        # =====================================================
        # 🧠 NORMALIZED OUTPUT (ВАЖНО ДЛЯ MEGABOT)
        # =====================================================

        try:
            content = data["choices"][0]["message"]["content"]
        except:
            content = None

        return {
            "raw": data,
            "text": content
        }

    except Exception as e:
        return {
            "error": str(e)
        }