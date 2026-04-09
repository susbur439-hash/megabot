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

    base_score = parent_exp.get("score", 50) if parent_exp else 50
    boost = max(5, int(base_score / 5 + random.randint(1, 6)))

    code = f"""def run(data):
    boost = {boost}

    data.setdefault("goal", {{"progress": 0}})
    data.setdefault("log", [])

    system_boost = data.get("boost", 1.0)
    boost = int(boost * system_boost)

    data["goal"]["progress"] += boost
    data["log"].append("module {new_id} executed | +" + str(boost))

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 🛠 IMPROVE MODULE (СТАБИЛЬНЫЙ)
# =========================
def improve_existing_module(module_name):
    path = os.path.join("modules", module_name + ".py")

    if not os.path.exists(path):
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()

        if "boost +=" in code:
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
# 🔥 EXECUTION (ФИНАЛ)
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

    best_module_name, best_score = get_best_module(data["experience"])
    best_exp = next((e for e in data["experience"] if e["module"] == best_module_name), None)

    # =========================
    # 🎯 DECISION SYSTEM
    # =========================

    if decision == "create_module":
        data["log"].append("🔥 create_module")

        module_used = create_new_module(best_exp)
        path = os.path.join("modules", module_used + ".py")
        data, success = run_python_module(path, data)

    elif decision == "run_module":
        data["log"].append("🚀 run_module")

        if best_module_name:
            module_used = best_module_name
            path = os.path.join("modules", module_used + ".py")
            data, success = run_python_module(path, data)
        else:
            data["log"].append("⚠️ no module → create")
            module_used = create_new_module()
            path = os.path.join("modules", module_used + ".py")
            data, success = run_python_module(path, data)

    elif decision == "improve_module":
        data["log"].append("🛠 improve_module")

        if best_module_name and improve_existing_module(best_module_name):
            module_used = best_module_name
            success = True
            data["goal"]["progress"] += 5
        elif best_module_name:
            module_used = best_module_name
            path = os.path.join("modules", module_used + ".py")
            data, success = run_python_module(path, data)

    elif decision == "generate_idea":
        data["log"].append("💡 idea")
        success = True

    else:
        data["log"].append("⚠️ fallback → create")
        module_used = create_new_module()
        path = os.path.join("modules", module_used + ".py")
        data, success = run_python_module(path, data)

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
            "delta": delta,
            "time": len(data["memory"])
        }
        data["experience"].append(exp)

        if not data.get("best_module") or score >= data["best_module"].get("score", 0):
            data["best_module"] = exp

    data["memory"].append(decision)

    data["memory"] = data["memory"][-100:]
    data["log"] = data["log"][-200:]

    save_to_memory(data)

    return data
