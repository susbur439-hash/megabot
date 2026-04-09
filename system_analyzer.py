import os
import json

ROOT = "."


def scan_files():
    report = {
        "files": [],
        "modules": [],
        "other": []
    }

    for root, dirs, files in os.walk(ROOT):
        for file in files:
            path = os.path.join(root, file)

            if file.endswith(".py"):
                report["files"].append(path)

                if "modules" in root:
                    report["modules"].append(path)
                else:
                    report["other"].append(path)

    return report


def check_core_modules(modules):
    required = [
        "analysis.py",
        "decision.py",
        "execution.py",
        "goals.py",
        "system_guard.py",
        "self_improver.py"
    ]

    found = [os.path.basename(m) for m in modules]

    status = {}
    for r in required:
        status[r] = "OK" if r in found else "MISSING"

    return status


def analyze_memory():
    if not os.path.exists("memory.json"):
        return {"status": "no memory file"}

    try:
        with open("memory.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "memory_size": len(data.get("memory", [])),
            "experience_size": len(data.get("experience", [])),
            "last_score": data.get("evaluation", {}).get("score", None),
            "last_delta": data.get("last_delta", None)
        }

    except Exception as e:
        return {"error": str(e)}


def detect_loops(data):
    memory = data.get("memory", [])

    if len(memory) < 5:
        return "not enough data"

    last = memory[-5:]

    if len(set(last)) == 1:
        return "⚠️ loop detected"

    return "ok"


def analyze_behavior():
    if not os.path.exists("memory.json"):
        return "no data"

    try:
        with open("memory.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        loop_status = detect_loops(data)

        return {
            "loop": loop_status
        }

    except:
        return "error"


def main():
    print("\n=== 🔍 FULL SYSTEM ANALYSIS ===\n")

    report = scan_files()

    print(f"📁 Всего файлов: {len(report['files'])}")
    print(f"🧠 Модулей: {len(report['modules'])}")
    print(f"📄 Остальные: {len(report['other'])}\n")

    print("=== 📦 MODULES LIST ===")
    for m in report["modules"]:
        print(m)

    print("\n=== 🧩 CORE CHECK ===")
    core = check_core_modules(report["modules"])
    for k, v in core.items():
        print(f"{k}: {v}")

    print("\n=== 💾 MEMORY ===")
    mem = analyze_memory()
    for k, v in mem.items():
        print(f"{k}: {v}")

    print("\n=== 🧠 BEHAVIOR ===")
    behavior = analyze_behavior()
    print(behavior)

    print("\n=== ⚠️ RECOMMENDATIONS ===")

    missing = [k for k, v in core.items() if v == "MISSING"]

    if missing:
        print("❗ Missing core modules:", missing)

    if isinstance(behavior, dict) and "loop" in behavior and "loop" in behavior["loop"]:
        print("❗ System stuck in loop → fix decision logic")

    if isinstance(mem, dict) and mem.get("experience_size", 0) < 5:
        print("❗ Weak learning → improve experience system")

    print("\n=== ✅ END ===\n")


if __name__ == "__main__":
    main()
