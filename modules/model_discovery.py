import os
import requests
import json

TOKEN = os.getenv("MODELS_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

urls = [
    "https://models.github.ai/catalog/models",
    "https://models.inference.ai.azure.com/models"
]

for url in urls:
    print("=" * 50)
    print("CHECK:", url)

    try:
        r = requests.get(url, headers=headers, timeout=30)

        print("STATUS:", r.status_code)

        try:
            data = r.json()
            print(json.dumps(data, indent=2))
        except:
            print(r.text)

    except Exception as e:
        print("ERROR:", e)