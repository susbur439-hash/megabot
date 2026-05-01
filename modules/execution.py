import os
import json
import importlib.util

from environment import run_environment


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
    except:
        pass


# =========================
# 📦 RUN MODULE
# =========================
def run_python_module(module_path, data):
    try:
        if not os.path.exists(module_path):
            data.setdefault("log", []).append(f"❌ module not found: {module_path}")
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
        data.setdefault("log", []).append(f"❌ module error: {e}")
        return data, False


# =========================
# 🚀 EXECUTION (ONLY RUN)
# =========================
def execution(data):

    memory = load_memory()

    for k, v in memory.items():
        if k not in data:
            data[k] = v

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    module_used = data.get("module")

    # 👉 execution НЕ думает — только выполняет
    if module_used:
        path = os.path.join("modules", module_used + ".py")
        data, ok = run_python_module(path, data)

        if ok:
            data["log"].append(f"🚀 executed: {module_used}")

    # 👉 внешний feedback (если есть)
    if data.get("log"):
        data, reward = run_environment(data, data["log"][-1])
        data["goal"]["progress"] += reward // 5

    # 👉 сохраняем опыт
    data["experience"].append({
        "module": module_used,
        "delta": data["goal"]["progress"]
    })

    save_to_memory(data)

    return data


# alias
def execute(data):
    return execution(data)
