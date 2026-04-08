import os
import random
import json
import importlib.util


# =========================
# 💾 SAVE
# =========================
def save_to_memory(data):
    try:
        with open("memory.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)


# =========================
# 🚀 RUN MODULE
# =========================
def run_python_module(module_path, data):
    try:
        if not os.path.exists(module_path):
            data["log"].append("❌ module not found")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)

        if spec is None or spec.loader is None:
            data["log"].append("❌ load failed")
            return data, False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            result = module.run(data)

            if isinstance(result, dict):
                return result, True

        data["log"].append("⚠️ invalid module result")
        return data, False

    except Exception as e:
        data["log"].append(f"❌ module error: {e}")
        return data, False


# =========================
# 🧠 BEST MODULE
# =========================
def get_best_module(experience):
    if not experience:
        return None, 0

    best = max(experience, key=lambda x: x.get("score", 0))
    return best.get("module"), best.get("score", 0)


# =========================
# 📁 MODULES
# =========================
def get_all_modules():
    if not os.path.exists("modules"):
        return []
    return [f for f in os.listdir("modules") if f.endswith(".py")]


# =========================
# 🧬 CREATE MODULE
# =========================
def create_new_module(parent=None):
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()

    ids = [
        int(m.replace("module_", "").replace(".py", ""))
        for m in modules if m.startswith("module_")
    ]

    new_id = max(ids, default=0) + 1
    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    base = parent.get("score", 50) if parent else 50
    boost = max(5, int(base / 6 + random.randint(0, 5)))

    code = f"""def run(data):
    boost = {boost}

    if "goal" not in data:
        data["goal"] = {{"progress": 0}}

    system_boost = data.get("boost", 1.0)
    boost = int(boost * system_boost)

    data["goal"]["progress"] += boost

    data.setdefault("log", [])
    data["log"].append("module {new_id} executed | +" + str(boost))

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 🛠 IMPROVE
# =========================
def improve_existing_module(module_name):
    path = os.path.join("modules", module_name + ".py")

    if not os.path.exists(path):
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()

        if "+ 3" in code:
            return False

        new_code = code.replace(
            "data[\"goal\"][\"progress\"] += boost",
            "data[\"goal\"][\"progress\"] += boost + 3"
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_code)

        return True

    except:
        return False


# =========================
# 📊 SCORE
# =========================
def calculate_score(before, after, success=True):
    if not success:
        return 10

    delta = after - before

    if delta <= 0:
        return 20
    elif delta < 5:
        return 60
    elif delta < 15:
        return 80
    else:
        return 100


# =========================
# 🔥 EXECUTION FIXED
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    before = data["goal"]["progress"]

    module_used = None
    success = False

    best_module, best_score = get_best_module(data["experience"])

    # =========================
    # 🔥 ГЛАВНАЯ ЛОГИКА (СТАБИЛЬНАЯ)
    # =========================

    # 1. Нет модулей → создать
    if not data["experience"]:
        data["log"].append("🔥 create first module")

        module_used = create_new_module()
        path = os.path.join("modules", module_used + ".py")
        data, success = run_python_module(path, data)

    # 2. Есть модуль → использовать
    else:
        if random.random() < 0.7:
            data["log"].append("🚀 run best module")

            module_used = best_module
            path = os.path.join("modules", best_module + ".py")
            data, success = run_python_module(path, data)

        else:
            data["log"].append("🛠 improve module")

            if improve_existing_module(best_module):
                module_used = best_module
                success = True
                data["goal"]["progress"] += 5
            else:
                module_used = best_module
                path = os.path.join("modules", best_module + ".py")
                data, success = run_python_module(path, data)

    # =========================
    # 📊 RESULT
    # =========================
    after = data["goal"]["progress"]
    delta = after - before
    data["last_delta"] = delta

    score = calculate_score(before, after, success)

    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score,
            "delta": delta,
            "time": len(data["memory"])
        })

    data["memory"].append(module_used or "none")

    data["memory"] = data["memory"][-100:]
    data["log"] = data["log"][-200:]

    save_to_memory(data)

    return data
