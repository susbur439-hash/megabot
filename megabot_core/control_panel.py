import json
from observer import scan_project
from analyzer import analyze
from execution import execute

def run():
    print("=== MEGABOT CORE ===")

    while True:
        cmd = input("\nscan / fix / exit:\n")

        if cmd == "exit":
            break

        elif cmd == "scan":
            report = scan_project(".")
            analysis = analyze(report)

            print("\n=== ANALYSIS ===")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))

        elif cmd == "fix":
            report = scan_project(".")
            analysis = analyze(report)

            actions = analysis.get("actions", [])
            result = execute(actions)

            print("\n=== FIX RESULT ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        else:
            print("unknown command")
