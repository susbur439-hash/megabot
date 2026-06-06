import os
import requests

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")

def ask_model(prompt: str):
"""
Отправка запроса в GitHub Models API
"""

if not GITHUB_TOKEN:
    return {"error": "MODELS_TOKEN not found"}

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
    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code != 200:
        return {
            "error": response.text,
            "status": response.status_code
        }

    data = response.json()

    # защита от пустого ответа
    if not data:
        return {"error": "empty response"}

    return data

except Exception as e:
    return {"error": str(e)}