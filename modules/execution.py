import os
import random
import json
import importlib.util

from environment import run_environment
from modules.control import control


# =========================
# 💾 SAFE GIT SAVE
# =========================
def save_to_git():
    try:
        os.system('git config --global user.name "megabot"')
        os.system('git config --global user.email "bot@megabot.ai"')

        os.system('git add .')
        os.system('git commit -m "Megabot auto update" || echo "No changes"')

        os.system('git pull --rebase origin main')
        os.system('git push origin main')

        print("✅ Git synced")

    except Exception as e:
        print("Git error:", e)


# =========================
# 💾 MEMORY
# =========================
def load_memory():
    try:
        if os.path.exists("memory.json"):
            with open("memory.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}


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
# 🔥 TASK FIX
# =========================
def get_task_text(data):
    task_value = data.get("task", "")

    if isinstance(task_value, dict):
        task_value = task_value.get("task", "")

    return str(task_value).lower()


# =========================
# 🔥 REAL ACTIONS
# =========================
def execute_real_action(data):
    task = get_task_text(data)

    try:
        os.makedirs("generated", exist_ok=True)
        os.makedirs("modules", exist_ok=True)

        if "файл" in task or data.get("strategy") == "force_file":
            filename = f"generated/file_{random.randint(1000,9999)}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(str(data.get("analysis", "no data")))

            save_to_git()

            data["log"].append(f"📁 файл создан: {filename}")
            data["goal"]["progress"] += 20
            return data, True

        if "модуль" in task or data.get("strategy") == "build_module":

            module_name = f"auto_{random.randint(1000,9999)}.py"
            path = os.path.join("modules", module_name)

            boost = random.randint(10, 25)

            code = f"""def run(data):
    data.setdefault("goal", {{"progress": 0}})
    data["goal"]["progress"] += {boost}
    data.setdefault("log", []).append("auto +{boost}")
    return data
"""

            with open(path, "w", encoding="utf-8") as f:
                f.write(code)

            save_to_git()

            data["log"].append(f"🧠 авто-модуль: {module_name}")
            data["goal"]["progress"] += 25
            return data, True

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
            data["log"].append(f"❌ module not found: {module_path}")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            result = module.run(data)
            if isinstance(result, dict):
                return result, True

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


def create_new_module(data):
    os.makedirs("modules", exist_ok=True)

    modules = [m for m in os.listdir("modules") if m.endswith(".py")]

    if len(modules) > 30:
        data["log"].append("🚨 module limit reached")
        return None

    name = f"module_{len(modules)+1}.py"
    path = os.path.join("modules", name)

    boost = random.randint(5, 15)

    code = f"""def run(data):
    data.setdefault("goal", {{"progress": 0}})
    data["goal"]["progress"] += {boost}
    data.setdefault("log", []).append("module +{boost}")
    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    save_to_git()

    return name[:-3]


# =========================
# 🚀 MAIN EXECUTION
# =========================
def execution(data):

    memory = load_memory()

    for k, v in memory.items():
        if k not in data:
            data[k] = v

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    ensure_env(data)

    task_text = get_task_text(data)

    if "file" in task_text:
        data["strategy"] = "force_file"
    elif "module" in task_text:
        data["strategy"] = "build_module"

    data = control(data)

    before = data["goal"]["progress"]
    best_module = get_best_module(data["experience"])

    module_used = None

    if best_module:
        path = os.path.join("modules", best_module + ".py")
        data, ok = run_python_module(path, data)
        if ok:
            module_used = best_module

    if not module_used:
        module_name = create_new_module(data)
        if module_name:
            path = os.path.join("modules", module_name + ".py")
            data, _ = run_python_module(path, data)
            module_used = module_name

    if data["goal"]["progress"] <= before:
        data, _ = execute_real_action(data)
        module_used = "real_action"

    if data.get("log"):
        data, reward = run_environment(data, data["log"][-1])
        data["goal"]["progress"] += reward // 5

    data["experience"].append({
        "module": module_used,
        "score": 50,
        "delta": data["goal"]["progress"] - before
    })

    save_to_memory(data)

    return data


# 🔥 ВАЖНО: АЛИАС ДЛЯ ИМПОРТА
def execute(data):
    return execution(data)
