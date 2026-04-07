import os
import importlib.util
import random
import json


# =========================
# 💾 СОХРАНЕНИЕ
# =========================
def save_to_memory(data):
    try:
        with open("memory.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass


# =========================
# 🚀 ЗАПУСК МОДУЛЯ
# =========================
def run_python_module(module_path, data):
    try:
        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            return module.run(data)
        else:
            data["log"].append("⚠️ module has no run()")
            return data

    except Exception as e:
        data["log"].append(f"❌ module error: {e}")
        return data


# =========================
# 📁 СПИСОК
# =========================
def get_all_modules():
    if not os.path.exists("modules"):
        return []
    return [f for f in os.listdir("modules") if f.endswith(".py")]


# =========================
# 🧠 ТОП МОДУЛИ
# =========================
def get_top_modules(experience, n=3):
    valid = [e for e in experience if isinstance(e, dict)]
    return sorted(valid, key=lambda x: x.get("score", 0), reverse=True)[:n]


# =========================
# 🧠 ЛУЧШИЙ
# =========================
def get_best_module(experience):
    if not experience:
        return None, 0

    best = max(experience, key=lambda x: x.get("score", 0))
    return best.get("module"), best.get("score", 0)


# =========================
# 🧬 СОЗДАНИЕ
# =========================
def create_new_module(parent=None):
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()
    new_id = len(modules) + 1

    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    if parent:
        base = parent.get("score", 50)
        boost = max(1, int(base / 10))
    else:
        boost = random.randint(3, 10)

    behavior = random.choice(["aggressive", "balanced", "safe"])

    code = f"""def run(data):
    boost = {boost}
    behavior = "{behavior}"

    if behavior == "aggressive":
        boost = int(boost * 1.5)
    elif behavior == "safe":
        boost = int(boost * 0.7)

    data["goal"]["progress"] += boost
    data["log"].append(f"module {new_id} | behavior={{behavior}} | boost={{boost}}")

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 📊 НОРМАЛЬНАЯ ОЦЕНКА
# =========================
def calculate_score(before, after):
    delta = after - before

    if delta <= 0:
        return 10
    elif delta < 5:
        return 40
    elif delta < 10:
        return 70
    else:
        return 100


# =========================
# 🛠 УЛУЧШЕНИЕ (БЕЗ ЛОМАНИЯ)
# =========================
def improve_existing_module(module_name):
    path = os.path.join("modules", module_name + ".py")

    if not os.path.exists(path):
        return False

    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # аккуратное улучшение
    if "boost =" in code:
        code = code.replace("boost =", "boost = int(")
        code = code.replace("\n\n    return data", ")\n\n    return data")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return True


# =========================
# 🧹 ЧИСТКА
# =========================
def cleanup_modules(data):
    if len(data["experience"]) < 5:
        return

    # удаляем слабые
    data["experience"] = [e for e in data["experience"] if e["score"] >= 40]

    # ограничиваем
    data["experience"] = sorted(
        data["experience"],
        key=lambda x: x["score"],
        reverse=True
    )[:20]


# =========================
# 🔥 EXECUTION
# =========================
def execution(data):

    print("EXECUTION:", data.get("result"))

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    module_used = None

    best_module, best_score = get_best_module(data["experience"])

    # 🎯 выбор действия (без хаоса)
    if data["decision"] == "run_module" and best_module:
        action = "run_best"
    elif data["decision"] == "improve_module" and best_module:
        action = "improve"
    else:
        action = "create"

    before = data["goal"].get("progress", 0)

    # =========================
    # CREATE
    # =========================
    if action == "create":
        module_used = create_new_module()
        path = os.path.join("modules", module_used + ".py")
        data = run_python_module(path, data)
        data["result"] = "module created"

    # =========================
    # RUN BEST
    # =========================
    elif action == "run_best":
        module_used = best_module
        path = os.path.join("modules", module_used + ".py")
        data = run_python_module(path, data)
        data["result"] = "module executed"

    # =========================
    # IMPROVE
    # =========================
    elif action == "improve":
        if improve_existing_module(best_module):
            module_used = best_module
            data["goal"]["progress"] += 3
            data["result"] = "module improved"
        else:
            data["result"] = "improve failed"

    after = data["goal"].get("progress", 0)

    # 📊 оценка
    score = calculate_score(before, after)

    # =========================
    # 🧠 ОБУЧЕНИЕ (НОВОЕ!)
    # =========================
    data.setdefault("learning", [])
    data["learning"].append({
        "task": data.get("task"),
        "action": action,
        "module": module_used,
        "delta": after - before,
        "score": score
    })

    data["learning"] = data["learning"][-50:]

    # =========================
    # 🧠 EXPERIENCE
    # =========================
    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score,
            "time": len(data["memory"])
        })

    # =========================
    # 🧹 CLEANUP
    # =========================
    cleanup_modules(data)

    # =========================
    # 🧠 MEMORY
    # =========================
    data["memory"].append(data["decision"])
    data["memory"] = data["memory"][-100:]

    # =========================
    # 📘 LOG
    # =========================
    data["log"].append(
        f"execution: {action} | module: {module_used} | delta: {after - before} | score: {score} | best: {best_module}({best_score})"
    )

    save_to_memory(data)

    return data
