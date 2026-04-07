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
        if not os.path.exists(module_path):
            data["log"].append("❌ module file not found")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)

        if spec is None or spec.loader is None:
            data["log"].append("❌ failed to load module")
            return data, False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            result = module.run(data)

            if not isinstance(result, dict):
                data["log"].append("⚠️ module returned invalid data")
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
# 🧠 IDEA GENERATOR (🔥 НОВОЕ)
# =========================
def generate_idea_module():
    boost = random.randint(4, 12)
    behavior = random.choice(["aggressive", "balanced", "safe"])

    return boost, behavior


# =========================
# 🧬 CREATE MODULE
# =========================
def create_new_module(parent=None):
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()

    existing_ids = [
        int(m.replace("module_", "").replace(".py", ""))
        for m in modules if m.startswith("module_")
    ]

    new_id = max(existing_ids, default=0) + 1

    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    # 🔥 идея генерации
    if parent:
        base = parent.get("score", 50)
        boost = max(2, int(base / 10 + random.randint(-3, 4)))
    else:
        boost, _ = generate_idea_module()

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
def calculate_score(before, after, success=True):
    delta = after - before

    if not success:
        return 10

    if delta <= 0:
        return 20
    elif delta < 5:
        return 50
    elif delta < 10:
        return 75
    else:
        return 100


# =========================
# 🛠 SAFE IMPROVE
# =========================
def improve_existing_module(module_name):
    path = os.path.join("modules", module_name + ".py")

    if not os.path.exists(path):
        return False

    try:
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

    except Exception:
        return False


# =========================
# 🧹 CLEANUP
# =========================
def cleanup_modules(data):
    exp = [e for e in data.get("experience", []) if isinstance(e, dict)]

    if len(exp) < 5:
        return

    good = [e for e in exp if e.get("score", 0) >= 40]
    bad = [e for e in exp if e.get("score", 0) < 40]

    for b in bad:
        path = os.path.join("modules", b.get("module", "") + ".py")
        if os.path.exists(path):
            os.remove(path)
            data["log"].append(f"🗑 removed {b.get('module')}")

    data["experience"] = sorted(
        good,
        key=lambda x: x.get("score", 0),
        reverse=True
    )[:20]


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
    decision = data.get("decision")

    before = data["goal"].get("progress", 0)

    # =========================
    # 🎯 ACTION MAPPING
    # =========================
    if decision == "run_module" and best_module:
        action = "run"
    elif decision == "improve_module" and best_module:
        action = "improve"
    elif decision == "generate_idea":
        action = "idea"
    else:
        action = "create"

    # =========================
    # 💡 IDEA
    # =========================
    if action == "idea":
        boost, behavior = generate_idea_module()

        data["goal"]["progress"] += boost
        success = True
        module_used = "idea"

        data["log"].append(f"💡 idea | behavior={behavior} | boost={boost}")
        data["result"] = "idea generated"

    # =========================
    # CREATE
    # =========================
    elif action == "create":
        parent = {"module": best_module, "score": best_score} if best_module else None

        module_used = create_new_module(parent)
        path = os.path.join("modules", module_used + ".py")

        data, success = run_python_module(path, data)
        data["result"] = "module created"

    # =========================
    # RUN
    # =========================
    elif action == "run":
        path = os.path.join("modules", best_module + ".py")

        module_used = best_module
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

    delta = after - before
    data["last_delta"] = delta
    data["success"] = success

    # =========================
    # SCORE
    # =========================
    score = calculate_score(before, after, success)

    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score,
            "time": len(data["memory"])
        })

    cleanup_modules(data)

    data["memory"].append(decision)
    data["memory"] = data["memory"][-100:]

    data["log"] = data["log"][-200:]

    data["log"].append(
        f"execution: {action} | module: {module_used} | success: {success} | delta: {delta} | score: {score}"
    )

    save_to_memory(data)

    return data
