import os
import json

ROOT = "."


# =========================
# 📦 SCAN SYSTEM
# =========================
def scan_files():
    structure = {}

    for root, dirs, files in os.walk(ROOT):
        # игнорируем мусор
        if ".git" in root:
            continue
        structure[root] = files

    return structure


# =========================
# 🧠 STRUCTURE CHECK
# =========================
def check_structure(structure):
    issues = []
    warnings = []
    ok = []

    found_paths = set(structure.keys())
    all_files = []
    for files in structure.values():
        all_files.extend(files)

    # =========================
    # 📁 CORE ARCHITECTURE (реальная)
    # =========================
    expected_dirs = [
        "modules",
        "meta",
        "megabot_core"
    ]

    for d in expected_dirs:
        if not any(d in path for path in found_paths):
            warnings.append(f"⚠️ missing optional layer: {d}")
        else:
            ok.append(f"✅ layer present: {d}")

    # =========================
    # ⚙️ CORE ENTRY POINT
    # =========================
    expected_files = ["main.py"]

    for f in expected_files:
        if f not in all_files:
            issues.append(f"❌ missing entry file: {f}")
        else:
            ok.append(f"✅ entry file exists: {f}")

    # =========================
    # 🧩 MODULE SYSTEM CHECK
    # =========================
    module_count = len([f for f in all_files if f.startswith("module_")])

    if module_count == 0:
        warnings.append("⚠️ no generated modules found (module_###)")
    else:
        ok.append(f"✅ generated modules: {module_count}")

    return issues, warnings, ok


# =========================
# 🧪 LOGIC CHECK
# =========================
def check_logic():
    warnings = []

    if not os.path.exists("memory.json"):
        warnings.append("⚠️ memory.json missing (state will be ephemeral)")
    else:
        ok_size = os.path.getsize("memory.json")
        if ok_size == 0:
            warnings.append("⚠️ memory.json is empty")

    return warnings


# =========================
# 📊 SYSTEM SCORE
# =========================
def system_score(issues, warnings):
    score = 100

    score -= len(issues) * 25
    score -= len(warnings) * 5

    return max(0, min(100, score))


# =========================
# 🧠 OBSERVER CORE
# =========================
def run_observer():
    print("\n🧠 OBSERVER START\n")

    structure = scan_files()

    issues, warnings, ok = check_structure(structure)
    logic_warnings = check_logic()

    warnings.extend(logic_warnings)

    score = system_score(issues, warnings)

    # =========================
    # 📊 STRUCTURE OUTPUT
    # =========================
    print("📦 STRUCTURE SUMMARY:\n")
    for path, files in structure.items():
        print(f"{path}: {len(files)} files")

    # =========================
    # ❌ ISSUES
    # =========================
    print("\n❌ CRITICAL ISSUES:")
    if not issues:
        print("none")
    else:
        for i in issues:
            print(i)

    # =========================
    # ⚠️ WARNINGS
    # =========================
    print("\n⚠️ WARNINGS:")
    if not warnings:
        print("none")
    else:
        for w in warnings:
            print(w)

    # =========================
    # ✅ OK STATE
    # =========================
    print("\n✅ HEALTHY PARTS:")
    for o in ok:
        print(o)

    # =========================
    # 🏁 SCORE
    # =========================
    print(f"\n🏁 SYSTEM HEALTH: {score}/100")

    if score > 80:
        print("🟢 SYSTEM STABLE")
    elif score > 50:
        print("🟡 SYSTEM DEGRADED")
    else:
        print("🔴 SYSTEM CRITICAL")

    print("\n🧠 OBSERVER END\n")


if __name__ == "__main__":
    run_observer()
