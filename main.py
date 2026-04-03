import requests
import random

def log(message):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")

# ================= AI =================
HF_API_KEY = "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"

def ask_ai(question):
    API_URL = "https://api-inference.huggingface.co/models/gpt2"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {"inputs": question}

    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        return response.json()[0]["generated_text"]
    except:
        return "Ошибка AI"

# ================= СИСТЕМА =================
class SelfBuildingSystem:
    def __init__(self):
        self.components = ['initial_algorithm']
        self.performance_data = []

    def analyze_system(self):
        print(f"\nКомпоненты: {self.components}")
        performance = random.uniform(0, 1)
        self.performance_data.append(performance)

        print(f"Производительность: {performance}")

        if performance < 0.5:
            print("⚠️ Улучшаем систему...")
            self.upgrade_system()

    def upgrade_system(self):
        new_component = f"algo_{len(self.components)+1}"
        self.components.append(new_component)
        print(f"✅ Добавлен: {new_component}")

    def add_new_function(self):
        if len(self.performance_data) > 3 and self.performance_data[-1] > 0.7:
            print("\n🤖 AI думает...")
            idea = ask_ai("Придумай способ заработка в интернете")
            print("💡 Идея:", idea)

    def start(self):
        print("🚀 Мегабот запущен\n")

        for i in range(5):
            print(f"\n=== Шаг {i+1} ===")
            self.analyze_system()
            self.add_new_function()

        print("\n✅ Готово")

# ================= ЗАПУСК =================
if __name__ == "__main__":
    bot = SelfBuildingSystem()
    bot.start()
# run
