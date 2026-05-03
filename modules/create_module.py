import os
import random


def generate_module_name():
    return f"module_auto_{random.randint(1000, 999999)}"


def generate_module_code(name):
    return f'''
def run(data):
    data.setdefault("log", []).append("⚙️ {name} working")

    goal = data.setdefault("goal", {{}})
    goal["progress"] = goal.get("progress", 0) + 10

    # простая "полезная" логика
    if "value" not in data:
        data["value"] = 0

    data["value"] += 1

    data["log"].append("📈 progress increased")

    return data
'''


def create_module(data):
    data.setdefault("log", [])

    try:
        os.makedirs("modules", exist_ok=True)

        name = generate_module_name()
        path = os.path.join("modules", name + ".py")

        code = generate_module_code(name)

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        data["module"] = name

        data["log"].append(f"🧩 created module: {name}")

        return data, True

    except Exception as e:
        data["log"].append(f"❌ create_module error: {e}")
        return data, False


# универсальный интерфейс
def run(data):
    data, success = create_module(data)
    return data
