import os
import random
import json
import importlib.util
from environment import run_environment


def save_to_memory(data):
    try:
        with open("memory.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)


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


def is_task_completed(data):
    return False  # отключаем авто-стоп (важно для развития)


def execute_real_action(data):
    task = data.get("task", "").lower()

    try:
        os.makedirs("generated", exist_ok=True)
        os.makedirs("modules", exist_ok=True)

        if "создай файл" in task or "create file" in task:
            filename = f"generated/file_{random.randint(1000,9999)}.txt"

            content = "Megabot result:\n"
            content += str(data.get("analysis", "no data"))

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            data["log"].append(f"📁 создан файл: {filename}")
            data["goal"]["progress"] += 20
            return data, True

        if "создай модуль" in task or "create module" in task:
            module_name = f"auto_module_{random.randint(1000,9999)}.py"
            path = os.path.join("modules", module_name)

            code = f"""def run(data):
    data.setdefault("log", [])
    data.setdefault("goal", {{"progress": 0}})

    data["goal"]["progress"] += {random.randint(5,15)}
    data["log"].append("⚙️ auto module executed")

    return data
"""

            with open(path, "w", encoding="utf-8") as f:
                f.write(code)

            data["log"].append(f"🧠 создан модуль: {module_name}")
            data["goal"]["progress"] += 25
            return data, True

        if "отчет" in task or "report" in task:
            filename = f"generated/report_{random.randint(1000,9999)}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            data["log"].append(f"📊 отчет сохранен: {filename}")
            data["goal"]["progress"] += 15
            return data, True

        data["log"].append("⚙️ базовое действие")
        data["goal"]["progress"] += 5
        return data, True

    except Exception as e:
        data["log"].append(f"❌ real action error: {e}")
        return data, False


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


def get_best_module(experience):
    valid = [x for x in experience if x.get("module") not in (None, "real_action")]

    if not valid:
        return None, 0

    best = max(valid, key=lambda x: x.get("score", 0))
    return best.get("module"), best.get("score", 0)


def get_all_modules():
    if not os.path.exists("modules"):
        return []
    return [f for f in os.listdir("modules") if f.endswith(".py")]


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

    boost = random.randint(5, 12)

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


def mutate_module(module_name):
    return create_new_module()


def apply_repeat_penalty(data, module_used):
    if len(data["experience"]) < 1:
        return

    last = data["experience"][-1]["module"]

    if last == module_used:
        data["env"]["entropy"] += 2
        data["log"].append("♻️ repeat penalty")


def calculate_score(data, before, after):
    env = data.get("env", {})

    delta = after - before

    score = 0
    score += delta * 5
    score += env.get("knowledge", 0) * 2
    score += env.get("success", 0) * 2

    score -= env.get("fail", 0) * 5
    score -= env.get("entropy", 0)

    return max(0, min(100, score))


def execution(data):

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})
    data.setdefault("repeat_count", 0)

    ensure_env(data)

    before = data["goal"]["progress"]

    task = data.get("task", "").lower()

    # 🔥 КЛЮЧЕВОЕ: ПРИНУДИТЕЛЬНОЕ ДЕЙСТВИЕ
    if "создай файл" in task or "create file" in task:
        data["log"].append("🎯 forced file creation")
        data, _ = execute_real_action(data)

    if "создай модуль" in task or "create module" in task:
        data["log"].append("🎯 forced module creation")
        data, _ = execute_real_action(data)

    module_used = None
    best_module, best_score = get_best_module(data["experience"])

    if len(data["experience"]) >= 2:
        if data["experience"][-1]["module"] == data["experience"][-2]["module"]:
            data["repeat_count"] += 1
        else:
            data["repeat_count"] = 0

    force_explore = data["repeat_count"] >= 2 or data["env"]["entropy"] > 10

    if best_module and not force_explore:
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

    after = data["goal"]["progress"]

    apply_repeat_penalty(data, module_used)

    if data["env"]["entropy"] > 15:
        data["env"]["entropy"] -= 5
        data["log"].append("🧹 entropy cleanup")

    if data.get("log"):
        data, reward = run_environment(data, data["log"][-1])
        data["goal"]["progress"] += reward // 5
        data["log"].append(f"🌍 reward: {reward}")

    after = data["goal"]["progress"]
    score = calculate_score(data, before, after)

    data["experience"].append({
        "module": module_used,
        "score": score,
        "delta": after - before
    })

    data["memory"].append("execution")

    data["memory"] = data["memory"][-100:]
    data["log"] = data["log"][-200:]

    save_to_memory(data)

    return data
    
