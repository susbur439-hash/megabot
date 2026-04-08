import os
import json


def load_memory():
    if not os.path.exists("memory.json"):
        return {}

    try:
        with open("memory.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_memory(data):
    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ensure_modules_exist():
    os.makedirs("modules", exist_ok=True)

    files = [f for f in os.listdir("modules") if f.endswith(".py")]

    if files:
        return False  # уже есть

    # создаём базовый модуль
    code = """def run(data):
    data.setdefault("goal", {"progress": 0})
    data.setdefault("log", [])

    boost = 10
    data["goal"]["progress"] += boost

    data["log"].append("🔥 base module executed | +10")

    return data
"""

    with open("modules/module_1.py", "w", encoding="utf-8") as f:
        f.write(code)

    return True


def fix_experience(data):
    exp = data.get("experience", [])

    if exp:
        return False

    # если нет опыта — создаём искусственный
    data["experience"] = [{
        "module": "module_1",
        "score": 80,
        "delta": 10,
        "time": 0
    }]

    data.setdefault("log", []).append("🧠 experience injected")

    return True


def fix_decision_loop(data):
    memory = data.get("memory", [])

    if memory.count("generate_idea") >= 3:
        data["decision"] = "create_module"
        data.setdefault("log", []).append("🛑 loop fixed → force create_module")
        return True

    return False


def repair_system():
    data = load_memory()

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])

    fixes = []

    if ensure_modules_exist():
        fixes.append("MODULE_CREATED")

    if fix_experience(data):
        fixes.append("EXPERIENCE_FIXED")

    if fix_decision_loop(data):
        fixes.append("LOOP_FIXED")

    save_memory(data)

    print("=== SYSTEM REPAIR ===")
    print("Fixes applied:", fixes if fixes else "none")


if __name__ == "__main__":
    repair_system()
