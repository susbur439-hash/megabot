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
# 🧠 BEST MODULE
# =========================
def get_best_module(experience):
    valid = [e for e in experience if isinstance(e, dict)]

    if not valid:
        return None, 0

    module_scores = {}

    for e in valid:
        name = e.get("module")
        score = e.get("score", 0)
        module_scores.setdefault(name, []).append(score)

    best_module = None
    best_value = -1

    for name, scores in module_scores.items():
        avg = sum(scores) / len(scores)
        recent = scores[-1]
        stability = 1 / (1 + abs(avg - recent))

        value = avg * 0.5 + recent * 0.3 + stability * 20

        if value > best_value:
            best_value = value
            best_module = name

    return best_module, best_value


# =========================
# 💡 IDEA
# =========================
def generate_idea_module():
    boost = random.randint(4, 12)
    return boost


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

    base = parent.get("score", 50) if parent else 50
    boost = max(3, int(base / 8 + random.randint(-2, 5)))

    code = f"""def run(data):
    boost = {boost}

    if "goal" not in data:
        data["goal"] = {{"progress": 0}}

    system_boost = data.get("boost", 1.0)
    boost = int(boost * system_boost)

    data["goal"]["progress"] += boost

    data.setdefault("log", [])
    data["log"].append(f"module {new_id} | boost={{boost}}")

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 🛠 IMPROVE
# =========================
def improve_existing_module(module_name):
    path = os.path.join("modules", module_name + ".py")

    if not os.path.exists(path):
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()

        if "+ 2" in code:
            return False

        new_code = code.replace(
            "data[\"goal\"][\"progress\"] += boost",
            "data[\"goal\"][\"progress\"] += boost + 2"
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_code)

        return True

    except Exception:
        return False


# =========================
# 📊 SCORE
# =========================
def calculate_score(before, after, success=True):
    if not success:
        return 5

    delta = after - before

    if delta <= 0:
        return 20
    elif delta < 5:
        return 50
    elif delta < 15:
        return 80
    else:
        return 100


# =========================
# 🔥 IDEAL EXECUTION
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    decision = data.get("decision")
    before = data["goal"].get("progress", 0)

    module_used = None
    success = False

    best_module, best_score = get_best_module(data["experience"])

    # 🔥 ЖЁСТКАЯ СИНХРОНИЗАЦИЯ
    if decision not in ["create_module", "run_module", "improve_module", "generate_idea"]:
        data["log"].append(f"❌ invalid decision → fallback to create_module")
        decision = "create_module"

    data["log"].append(f"🎯 EXECUTE: {decision}")

    # 🔥 ЕСЛИ НЕТ МОДУЛЕЙ — СОЗДАЁМ
    if not data["experience"]:
        decision = "create_module"
        data["log"].append("🔥 FORCE CREATE (no modules)")

    # ⚡ АНТИ-СТАГНАЦИЯ
    if data.get("last_delta", 1) <= 0:
        data["boost"] = data.get("boost", 1.0) * 1.3
        data["log"].append("⚡ anti-stagnation")
    else:
        data["boost"] = max(1.0, data.get("boost", 1.0) * 0.95)

    # =========================
    # 🔥 ЛОГИКА
    # =========================

    if decision == "generate_idea":
        boost = generate_idea_module()
        boost = int(boost * data.get("boost", 1.0))
        data["goal"]["progress"] += boost
        success = True

    elif decision == "create_module":
        module_used = create_new_module(
            {"module": best_module, "score": best_score} if best_module else None
        )

        path = os.path.join("modules", module_used + ".py")
        data, success = run_python_module(path, data)

        data["goal"]["progress"] += 5

    elif decision == "run_module":
        if best_module:
            module_used = best_module
            path = os.path.join("modules", best_module + ".py")
            data, success = run_python_module(path, data)
        else:
            data["log"].append("⚠️ no module → fallback create")
            decision = "create_module"
            module_used = create_new_module()
            path = os.path.join("modules", module_used + ".py")
            data, success = run_python_module(path, data)

    elif decision == "improve_module":
        if best_module and improve_existing_module(best_module):
            module_used = best_module
            data["goal"]["progress"] += 6
            success = True
        else:
            data["log"].append("⚠️ improve failed → run module")
            decision = "run_module"

    # =========================
    # 📊 DELTA
    # =========================
    after = data["goal"].get("progress", 0)
    delta = after - before
    data["last_delta"] = delta

    # =========================
    # 📊 SCORE
    # =========================
    score = calculate_score(before, after, success)

    # =========================
    # 💾 EXPERIENCE
    # =========================
    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score,
            "delta": delta,
            "time": len(data["memory"])
        })

    # =========================
    # 💾 MEMORY
    # =========================
    if decision:
        data["memory"].append(decision)

    data["memory"] = data["memory"][-100:]
    data["log"] = data["log"][-200:]

    save_to_memory(data)

    return data
