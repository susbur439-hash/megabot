import os
import random
import json
import importlib.util
from environment import run_environment


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
# 🛡 SAFE ENV INIT
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
# 🎯 CHECK TASK COMPLETE
# =========================
def is_task_completed(data):
    task = data.get("task", "").lower()

    if "создай файл" in task:
        return os.path.exists("test.txt")

    return False


# =========================
# ⚙️ REAL ACTION
# =========================
def execute_real_action(data):
    task = data.get("task", "").lower()

    try:
        if "создай файл" in task:
            filename = "test.txt"

            content = "Результат анализа:\n"
            content += data.get("analysis", "нет данных")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            data["log"].append(f"📁 файл {filename} создан")
            data["goal"]["progress"] += 50
            return data, True

        data["goal"]["progress"] += 5
        data["log"].append("⚙️ базовое действие")
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
# 🧠 BEST MODULE
# =========================
def get_best_module(experience):
    valid = [x for x in experience if x.get("module") not in (None, "real_action")]

    if not valid:
        return None, 0

    best = max(valid, key=lambda x: x.get("score", 0))
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
def create_new_module():
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

    boost = random.randint(5, 15)

    code = f"""def run(data):
    data.setdefault("goal", {{"progress": 0}})
    data.setdefault("log", [])

    data["goal"]["progress"] += {boost}
    data["log"].append("module {new_id} | +{boost}")

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 🔁 REPEAT PENALTY (смягчён)
# =========================
def apply_repeat_penalty(data, module_used):
    if len(data["experience"]) < 1:
        return

    last = data["experience"][-1]["module"]

    if last == module_used:
        data["env"]["entropy"] += 1  # уменьшили штраф
        data["log"].append("♻️ repeat penalty")


# =========================
# 📊 SCORE (стабильный)
# =========================
def calculate_score(data, before, after):
    env = data.get("env", {})

    delta = after - before

    score = 0
    score += delta * 5
    score += env.get("knowledge", 0) * 2
    score += env.get("success", 0) * 2

    score -= env.get("fail", 0) * 3
    score -= env.get("entropy", 0) * 0.5

    return int(max(0, min(100, score)))


# =========================
# 🔥 EXECUTION FINAL (УЛУЧШЕН)
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})
    data.setdefault("best_result", {"score": 0, "progress": 0})
    data.setdefault("last_used", None)

    ensure_env(data)

    before = data["goal"]["progress"]

    if is_task_completed(data):
        data["log"].append("✅ задача уже выполнена")
        return data

    module_used = None

    # === ВЫБОР СТРАТЕГИИ (анти-зацикливание) ===
    best_module, _ = get_best_module(data["experience"])

    if best_module and random.random() > 0.5:
        if data["last_used"] == best_module:
            data["log"].append("⚠️ avoid repeat exploit")
            best_module = None

    if best_module:
        data["log"].append(f"🚀 run best: {best_module}")
        path = os.path.join("modules", best_module + ".py")
        data, success = run_python_module(path, data)
        module_used = best_module
    else:
        data["log"].append("🧪 explore: create module")
        module_name = create_new_module()
        path = os.path.join("modules", module_name + ".py")
        data, success = run_python_module(path, data)
        module_used = module_name

    # === FALLBACK ===
    after = data["goal"]["progress"]

    if after == before:
        data["log"].append("🧠 fallback → real action")
        data, success = execute_real_action(data)
        module_used = "real_action"

    # === ENV ===
    ensure_env(data)
    apply_repeat_penalty(data, module_used)

    if data.get("log"):
        data, reward = run_environment(data, data["log"][-1])

        # ограничение падения
        if reward < -5:
            reward = -5

        data["goal"]["progress"] += reward // 5
        data["log"].append(f"🌍 reward: {reward}")

    # === СТАБИЛИЗАЦИЯ ===
    data["env"]["entropy"] *= 0.9
    data["env"]["entropy"] = int(data["env"]["entropy"])

    # === EXPERIENCE ===
    after = data["goal"]["progress"]
    score = calculate_score(data, before, after)

    # === ЗАЩИТА ОТ ДЕГРАДАЦИИ ===
    if score > data["best_result"]["score"]:
        data["best_result"]["score"] = score
        data["best_result"]["progress"] = after
    else:
        if score < data["best_result"]["score"] * 0.5:
            data["log"].append("🛑 rollback to best state")
            data["goal"]["progress"] = data["best_result"]["progress"]

    data["last_used"] = module_used

    data["experience"].append({
        "module": module_used,
        "score": score,
        "delta": after - before
    })

    data["memory"].append("execution")

    # лимиты
    data["memory"] = data["memory"][-100:]
    data["log"] = data["log"][-200:]

    save_to_memory(data)

    return data
