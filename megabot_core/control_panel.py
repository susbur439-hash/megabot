import json
from observer import scan_project
from analyzer import analyze

def run():
    print("=== MEGABOT CORE (SCAN MODE) ===")

    report = scan_project(".")
    analysis = analyze(report)

    print("\n=== FULL ANALYSIS ===")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

    print("\n⚠️ Никакие изменения НЕ выполнены")
    print("👉 Скинь этот отчёт в ChatGPT")
