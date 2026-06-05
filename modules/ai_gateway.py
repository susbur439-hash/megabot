import os
import requests

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")

def ask_model(prompt: str):
    """
    Отправка запроса в GitHub Models / API
    """

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    # ⚠️ endpoint может отличаться в зависимости от модели
    url = "https://models.inference.ai.azure.com/chat/completions"

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        return {"error": response.text}

    return response.json()