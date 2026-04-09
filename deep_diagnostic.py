import json
import os

def load():
    if os.path.exists("memory.json"):
        with open("memory.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def analyze(data):
    print("\n=== 🧠 DEEP DIAGNOSTIC ===\n")

    if not data:
        print("❌ Нет memory.json")
        return

    exp = data.get("experience", [])
    best = data.get("best_module")

    print("📊 Опыт:", len(exp))

    if best:
        print("🏆 Лучший модуль:", best.get("module"))
        print("📈 Его score:", best.get("score"))
    else:
        print("❌ Нет лучшего модуля")

    print("\n--- Последние 5 действий ---")
    for m in data.get("memory", [])[-5:]:
        print("•", m)

    print("\n--- Последние 10 логов ---")
    for l in data.get("log", [])[-10:]:
        print(l)

    print("\n--- Проверка конфликтов ---")

    last_decision = data.get("last_decision")
    strategy = data.get("strategy")
    last_delta = data.get("last_delta")

    print("decision:", last_decision)
    print("strategy:", strategy)
    print("delta:", last_delta)

    if best and last_decision == "create_module":
        print("\n❗ ПРОБЛЕМА: есть лучший модуль, но создается новый")

    if last_delta == 0:
        print("\n❗ ПРОБЛЕМА: нет прогресса")

    print("\n=== END ===")


if __name__ == "__main__":
    data = load()
    analyze(data)
