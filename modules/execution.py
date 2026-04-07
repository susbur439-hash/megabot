import os
import importlib.util
import random
import json


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
# 🚀 SAFE MODULE RUN
# =========================
def run_python_module(module_path, data):
    try:
        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            result = module.run(data)

            if result is None:
                data["log"].append("⚠️ module returned None")
                return data, False

            return result, True
        else:
            data["log"].append("⚠️ module has no run()")
            return data, False

    except Exception as e:
        data["log"].append(f"❌ module error: {e}")
        return data, False


# =========================
# 📁 MODULE LIST
# =========================
def get_all_modules():
    if not os.path.exists("modules"):
        return []
    return [f for f in os.listdir("modules") if f.endswith(".py")]


# =========================
# 🧠 BEST MODULE
# =========================
def get_best_module(experience):
    valid = [e for e in experience if isinstance(e, dict)]
    if not valid:
        return None, 0

    best = max(valid, key=lambda x: x.get("score", 0))
    return best.get("module"), best.get("score", 0)


# =========================
# 🧬 CREATE MODULE
# =========================
def create_new_module(parent=None):
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()
    new_id = len(modules) + 1

    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    if parent:
        base = parent.get("score", 50)
        boost = max(2, int(base / 10 + random.randint(-2, 3)))
    else:
        boost = random.randint(3, 10)

    behavior = random.choice(["aggressive", "balanced", "safe"])

    code = f"""def run(data):
    boost = {boost}
    behavior = "{behavior}"

    if "goal" not in data:
        data["goal"] = {{"progress": 0}}

    if behavior == "aggressive":
        boost = int(boost * 1.5)
    elif behavior == "safe":
        boost = int(boost * 0.7)

    data["goal"]["progress"] += boost

    data.setdefault("log", [])
    data["log"].append(f"module {new_id} | behavior={{behavior}} | boost={{boost}}")

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 📊 SCORE
# =========================
def calculate_score(before, after):
    delta = after - before

    if delta <= 0:
        return 5
    elif delta < 5:
        return 40
    elif delta < 10:
        return 70
    else:
        return 100


# =========================
# 🛠 SAFE IMPROVE
# =========================
def improve_existing_module(module_name):
    path = os.path.join("modules", module_name + ".py")

    if not os.path.exists(path):
        return False

    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    if "progress" not in code:
        return False

    new_code = code.replace(
        "data[\"goal\"][\"progress\"] += boost",
        "data[\"goal\"][\"progress\"] += boost + 1"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_code)

    return True


# =========================
# 🧹 CLEANUP
# =========================
def cleanup_modules(data):
    if len(data["experience"]) < 5:
        return

    good = [e for e in data["experience"] if e["score"] >= 40]
    bad = [e for e in data["experience"] if e["score"] < 40]

    for b in bad:
        path = os.path.join("modules", b["module"] + ".py")
        if os.path.exists(path):
            os.remove(path)
            data["log"].append(f"🗑 removed {b['module']}")

    data["experience"] = sorted(good, key=lambda x: x["score"], reverse=True)[:20]


# =========================
# 🔥 EXECUTION CORE
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    module_used = None
    success = False

    best_module, best_score = get_best_module(data["experience"])

    # 🎯 ACTION
    if data.get("decision") == "run_module" and best_module:
        action = "run"
    elif data.get("decision") == "improve_module" and best_module:
        action = "improve"
    else:
        action = "create"

    before = data["goal"].get("progress", 0)

    # =========================
    # CREATE
    # =========================
    if action == "create":
        parent = {"module": best_module, "score": best_score} if best_module else None

        module_used = create_new_module(parent)
        path = os.path.join("modules", module_used + ".py")

        data, success = run_python_module(path, data)
        data["result"] = "module created"

    # =========================
    # RUN
    # =========================
    elif action == "run":
        module_used = best_module
        path = os.path.join("modules", module_used + ".py")

        data, success = run_python_module(path, data)
        data["result"] = "module executed"

    # =========================
    # IMPROVE
    # =========================
    elif action == "improve":
        if improve_existing_module(best_module):
            module_used = best_module
            data["goal"]["progress"] += 2
            success = True
            data["result"] = "module improved"
        else:
            data["result"] = "improve failed"

    after = data["goal"].get("progress", 0)

    # =========================
    # 🔥 КРИТИЧЕСКИЙ ФИКС
    # =========================
    delta = after - before
    data["last_delta"] = delta
    data["success"] = success

    # =========================
    # SCORE
    # =========================
    score = calculate_score(before, after)

    if not success:
        score = max(5, score - 20)

    # =========================
    # EXPERIENCE
    # =========================
    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score,
            "time": len(data["memory"])
        })

    # =========================
    # CLEANUP
    # =========================
    cleanup_modules(data)

    # =========================
    # MEMORY
    # =========================
    data["memory"].append(data.get("decision"))
    data["memory"] = data["memory"][-100:]

    # =========================
    # LOG
    # =========================
    data["log"].append(
        f"execution: {action} | module: {module_used} | success: {success} | delta: {delta} | score: {score}"
    )

    save_to_memory(data)

    return data
