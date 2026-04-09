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
# ⚙️ REAL ACTION EXECUTOR
# =========================
def execute_real_action(data):
    task = data.get("task", "").lower()

    try:
        # 📁 СОЗДАНИЕ ФАЙЛА
        if "создай файл" in task:
            filename = "test.txt"

            if "test.txt" in task:
                filename = "test.txt"

            content = "Результат анализа:\n"
            content += data.get("analysis", "нет данных")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            data["log"].append(f"📁 файл {filename} создан и записан")
            data["goal"]["progress"] += 25
            return data, True

        # 💡 ЕСЛИ НЕ ПОНЯЛ — МАЛЕНЬКИЙ ПРОГРЕСС
        data["goal"]["progress"] += 5
        data["log"].append("⚙️ базовое действие выполнено")
        return data, True

    except Exception as e:
        data["log"].append(f"❌ real action error: {e}")
        return data, False


# =========================
# 🚀 RUN MODULE
# =========================
def run_python_module(module_path, data):
    try:
        if not os.path.exists(module_path):
            data["log"].append("❌ module not found")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)

        if not spec or not spec.loader:
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
# 🧬 CREATE MODULE (УЛУЧШЕН)
# =========================
def create_new_module(parent_exp=None):
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()

    ids = []
    for m in modules:
        if m.startswith("module_"):
            try:
                ids.append(int(m.replace("module_", "").replace(".py", "")))
            except:
                pass

    new_id = max(ids, default=0) + 1
    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    boost = random.randint(5, 20)

    code = f"""def run(data):
    data.setdefault("goal", {{"progress": 0}})
    data.setdefault("log", [])

    data["goal"]["progress"] += {boost}
    data["log"].append("module {new_id} executed | +{boost}")

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 📊 SCORE
# =========================
def calculate_score(before, after, success=True):
    if not success:
        return 10

    delta = after - before

    if delta <= 0:
        return 20
    elif delta < 10:
        return 60
    elif delta < 30:
        return 80
    else:
        return 100


# =========================
# 🔥 EXECUTION (НОВЫЙ)
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    decision = data.get("decision")
    before = data["goal"]["progress"]

    module_used = None
    success = False

    best_module_name, _ = get_best_module(data["experience"])

    # =========================
    # 🎯 DECISION
    # =========================

    if decision == "create_module":
        data["log"].append("🔥 create_module")

        module_used = create_new_module()
        path = os.path.join("modules", module_used + ".py")
        data, success = run_python_module(path, data)

    elif decision == "run_module":
        data["log"].append("🚀 run_module")

        if best_module_name:
            module_used = best_module_name
            path = os.path.join("modules", module_used + ".py")
            data, success = run_python_module(path, data)

    elif decision == "real_action":
        data["log"].append("⚙️ real_action")
        data, success = execute_real_action(data)

    else:
        data["log"].append("⚠️ fallback → real_action")
        data, success = execute_real_action(data)

    # =========================
    # 🔥 АНТИ-ЗАСТРЕВАНИЕ
    # =========================
    if data["goal"]["progress"] == before:
        data["log"].append("🧠 stagnation → force real action")
        data, success = execute_real_action(data)

    # =========================
    # 📊 RESULT
    # =========================
    after = data["goal"]["progress"]
    delta = after - before

    data["last_delta"] = delta

    score = calculate_score(before, after, success)

    if module_used:
        exp = {
            "module": module_used,
            "score": score,
            "delta": delta
        }
        data["experience"].append(exp)

    data["memory"].append(decision)

    data["memory"] = data["memory"][-100:]
    data["log"] = data["log"][-200:]

    save_to_memory(data)

    return data
