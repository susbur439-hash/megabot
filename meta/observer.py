import os
import json

ROOT = "."


def scan_files():
    structure = {}
    for root, dirs, files in os.walk(ROOT):
        structure[root] = files
    return structure


def check_structure(structure):
    issues = []
    warnings = []
    ok = []

    # базовые ожидания
    expected_dirs = ["modules", "meta"]

    for d in expected_dirs:
        if not any(d in path for path in structure):
            issues.append(f"❌ отсутствует папка: {d}")
        else:
            ok.append(f"✅ папка есть: {d}")

    # проверка ключевых файлов
    expected_files = ["main.py"]

    found_files = []
    for files in structure.values():
        found_files.extend(files)

    for f in expected_files:
        if f not in found_files:
            issues.append(f"❌ отсутствует файл: {f}")
        else:
            ok.append(f"✅ файл есть: {f}")

    return issues, warnings, ok


def check_logic():
    warnings = []

    # проверка памяти
    if not os.path.exists("memory.json"):
        warnings.append("⚠️ memory.json отсутствует")

    return warnings


def system_score(issues, warnings):
    score = 10
    score -= len(issues) * 2
    score -= len(warnings)

    if score < 0:
        score = 0

    return score


def run_observer():
    print("\n🧠 OBSERVER START\n")

    structure = scan_files()
    issues, warnings, ok = check_structure(structure)
    logic_warnings = check_logic()

    warnings.extend(logic_warnings)

    score = system_score(issues, warnings)

    print("📊 STRUCTURE:")
    for path, files in structure.items():
        print(f"{path}: {files}")

    print("\n❌ ПРОБЛЕМЫ:")
    for i in issues:
        print(i)

    print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
    for w in warnings:
        print(w)

    print("\n✅ ЧТО ХОРОШО:")
    for o in ok:
        print(o)

    print(f"\n🏁 SYSTEM SCORE: {score}/10")

    print("\n🧠 OBSERVER END\n")


if __name__ == "__main__":
    run_observer()
