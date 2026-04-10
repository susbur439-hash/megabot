import os
import random
import json
import importlib.util
from environment import run_environment
from modules.control import control


# =========================
# 💾 MEMORY
# =========================
def save_to_memory(data):
    try:
        with open("memory.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)


# =========================
# 🌍 ENV
# =========================
def ensure_env(data):
    env = data.setdefault("env", {})

    env.setdefault("energy", 100)
    env.setdefault("knowledge", 0)
    env.setdefault("success", 0)
    env.setdefault("fail", 0)
    env.setdefault("entropy", 0)
    env.setdefault("experience", 0)
    env.setdefault("level", 1)

    return env


# =========================
# 🔥 BREAK PATTERN
# =========================
def break_pattern(data):
    data["log"].append("💥 BREAK PATTERN ACTIVATED")

    module_name = create_new_module(boost_range=(15, 30))
    path = os.path.join("modules", module_name + ".py")

    data, _ = run_python_module(path, data)

    data["env"]["entropy"] = max(0, data["env"]["entropy"] - 3)
    data["goal"]["progress"] += random.randint(10, 20)

    return data, module_name


# =========================
# 🔥 REAL ACTIONS
# =========================
def execute_real_action(data):
    task = data.get("task", "").lower()

    try:
        os.makedirs("generated", exist_ok=True)
        os.makedirs("modules", exist_ok=True)

        # 📁 СОЗДАНИЕ ФАЙЛА
        if "файл" in task or data.get("strategy") == "force_file":
            filename = f"generated/file_{random.randint(1000,9999)}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(str(data.get("analysis", "no data")))

            data["log"].append(f"📁 файл создан: {filename}")
            data["goal"]["progress"] += 20
            return data, True

        # 🧠 СОЗДАНИЕ МОДУЛЯ
        if "модуль" in task or data.get("strategy") == "build_module":
            module_name = f"auto_{random.randint(1000,9999)}.py"
            path = os.path.join("modules", module_name)

            boost = random.randint(10, 20)

            code = f"""def run(data):
    data.setdefault("goal", {{"progress": 0}})
    data["goal"]["progress"] += {boost}
    data.setdefault("log", []).append("auto +{boost}")
    return data
"""

            with open(path, "w", encoding="utf-8") as f:
                f.write(code)

            data["log"].append(f"🧠 авто-модуль создан: {module_name}")
            data["goal"]["progress"] += 25
            return data, True

        # ⚙️ базовое действие
        data["goal"]["progress"] += 5
        return data, True

    except Exception as e:
        data["log"].append(f"❌ error: {e}")
        return data, False


# =========================
# 📦 MODULE EXECUTION
# =========================
def run_python_module(module_path, data):
    try:
        if not os.path.exists(module_path):
            data["log"].append("❌ module not found")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
        if not spec or not spec.loader:
            data["log"].append("❌ module load failed")
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
# 🧠 MODULE SYSTEM
# =========================
def get_best_module(experience):
    valid = [x for x in experience if x.get("module") not in ("real_action", None)]
    if not valid:
        return None
    return max(valid, key=lambda x: x.get("score", 0)).get("module")


def create_new_module(boost_range=(5, 15)):
    os.makedirs("modules", exist_ok=True)

    modules = [m for m in os.listdir("modules") if m.endswith(".py")]
    name = f"module_{len(modules)+1}.py"
    path = os.path.join("modules", name)

    boost = random.randint(*boost_range)

    code = f"""def run(data):
    data.setdefault("goal", {{"progress": 0}})
    data["goal"]["progress"] += {boost}
    data.setdefault("log", []).append("module +{boost}")
    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name[:-3]


# =========================
# 📊 SCORE
# =========================
def calculate_score(before, after):
    delta = after - before
    return max(0, min(100, delta * 5))


# =========================
# 🧠 LEARNING
# =========================
def update_knowledge(data, module, delta):
    kb = data.setdefault("knowledge_base", [])

    kb.append({
        "module": module,
        "delta": delta,
        "good": delta > 10
    })

    data["knowledge_base"] = kb[-50:]


# =========================
# 🚀 EXECUTION
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})
    data.setdefault("repeat_count", 0)

    ensure_env(data)

    # 🔥 авто-определение задачи
    task_text = data.get("task", "").lower()
    if "файл" in task_text:
        data["strategy"] = "force_file"
    elif "модуль" in task_text:
        data["strategy"] = "build_module"

    data = control(data)

    before = data["goal"]["progress"]

    best_module = get_best_module(data["experience"])
    module_used = None

    # 🔁 anti-loop
    if len(data["experience"]) >= 2:
        if data["experience"][-1]["module"] == data["experience"][-2]["module"]:
            data["repeat_count"] += 1
        else:
            data["repeat_count"] = 0

    stagnation = data["repeat_count"] >= 2
    high_entropy = data["env"]["entropy"] > 10

    # =========================
    # 🎯 SMART DECISION
    # =========================

    if data.get("strategy") in ["force_file", "build_module"]:
        data["log"].append(f"🎯 real action: {data['strategy']}")
        data, _ = execute_real_action(data)
        module_used = "real_action"

    elif stagnation:
        data["log"].append("💥 stagnation → real action")
        data["strategy"] = "force_file"
        data, _ = execute_real_action(data)
        module_used = "real_action"

    elif high_entropy:
        data, module_used = break_pattern(data)

    elif data.get("strategy") == "exploit" and best_module:
        path = os.path.join("modules", best_module + ".py")
        data, _ = run_python_module(path, data)
        module_used = best_module
        data["log"].append(f"🚀 exploit: {best_module}")

    else:
        module_name = create_new_module()
        path = os.path.join("modules", module_name + ".py")
        data, _ = run_python_module(path, data)
        module_used = module_name
        data["log"].append("🧪 explore")

    after = data["goal"]["progress"]

    # 🔥 fallback
    if after <= before:
        data["log"].append("🧠 fallback → real action")
        data["strategy"] = "force_file"
        data, _ = execute_real_action(data)
        module_used = "real_action"

    # 🌍 environment
    if data.get("log"):
        data, reward = run_environment(data, data["log"][-1])
        data["goal"]["progress"] += reward // 5

    after = data["goal"]["progress"]

    delta = after - before
    score = calculate_score(before, after)

    # 🧠 learning
    update_knowledge(data, module_used, delta)

    data["experience"].append({
        "module": module_used,
        "score": score,
        "delta": delta
    })

    data["log"] = data["log"][-200:]

    save_to_memory(data)

    return data
