import json
from observer import scan_project
from analyzer import analyze
from execution import execute


def run():
    print("=== MEGABOT CONTROL PANEL ===")

    while True:
        print("\nКоманды:")
        print("1. scan")
        print("2. fix (auto)")
        print("3. run JSON")
        print("4. exit")

        cmd = input("\n> ").strip()

        # 🔍 СКАН
        if cmd == "1" or cmd == "scan":
            report = scan_project(".")
            analysis = analyze(report)

            print("\n=== ANALYSIS ===")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))

        # 🛠 АВТО-ФИКС (осторожно)
        elif cmd == "2" or cmd == "fix":
            report = scan_project(".")
            analysis = analyze(report)

            actions = analysis.get("actions", [])
            result = execute(actions)

            print("\n=== FIX RESULT ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        # 🚀 ГЛАВНОЕ — РУЧНЫЕ КОМАНДЫ
        elif cmd == "3" or cmd == "run":
            print("\nВставь JSON (одной строкой):")

            try:
                raw = input(">> ")

                data = json.loads(raw)
                actions = data.get("actions", [])

                print("\n=== EXECUTION START ===")
                result = execute(actions)

                print("\n=== RESULT ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))

            except Exception as e:
                print("❌ Ошибка JSON:", e)

        # ❌ ВЫХОД
        elif cmd == "4" or cmd == "exit":
            print("Выход...")
            break

        else:
            print("❌ Неизвестная команда")
