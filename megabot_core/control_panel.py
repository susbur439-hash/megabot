import json
from observer import scan_project
from analyzer import analyze
from execution import execute


# =========================
# 🧠 SAFE CONFIG
# =========================
MAX_ACTIONS = 20


def safe_execute(actions):
    """
    Ограничение на безопасность исполнения
    """
    if not isinstance(actions, list):
        return {"error": "actions must be list"}

    if len(actions) > MAX_ACTIONS:
        return {
            "error": "too many actions",
            "limit": MAX_ACTIONS,
            "received": len(actions)
        }

    return execute(actions)


def run():
    print("=== MEGABOT CONTROL PANEL v2 ===")

    while True:
        print("\n📌 Доступные команды:")
        print("  scan       - анализ системы")
        print("  fix         - авто-исправление (safe)")
        print("  run         - выполнить JSON-команды")
        print("  exit        - выход")

        cmd = input("\n> ").strip().lower()

        # =========================
        # 🔍 SCAN MODE
        # =========================
        if cmd == "scan":
            print("\n🔍 Сканирование проекта...")
            report = scan_project(".")
            analysis = analyze(report)

            print("\n=== ANALYSIS RESULT ===")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))

        # =========================
        # 🛠 SAFE FIX MODE
        # =========================
        elif cmd == "fix":
            print("\n🛠 Запуск безопасного авто-фикса...")

            report = scan_project(".")
            analysis = analyze(report)

            actions = analysis.get("actions", [])

            # ⚠️ safety wrapper
            result = safe_execute(actions)

            print("\n=== FIX RESULT ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        # =========================
        # 🚀 MANUAL EXECUTION
        # =========================
        elif cmd == "run":
            print("\n📥 Вставь JSON-команду (одной строкой):")

            try:
                raw = input(">> ")
                data = json.loads(raw)

                if "actions" not in data:
                    print("❌ JSON должен содержать ключ 'actions'")
                    continue

                print("\n🚀 EXECUTION START")

                result = safe_execute(data["actions"])

                print("\n=== RESULT ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))

            except json.JSONDecodeError:
                print("❌ Ошибка: неправильный JSON")
            except Exception as e:
                print("❌ Ошибка:", str(e))

        # =========================
        # ❌ EXIT
        # =========================
        elif cmd == "exit":
            print("👋 Выход из панели управления")
            break

        else:
            print("❌ Неизвестная команда. Используй: scan / fix / run / exit")


if __name__ == "__main__":
    run()
