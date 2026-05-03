import os
import importlib.util
import random


# =========================
# 📦 MODULE RUNNER
# =========================
def run_python_module(module_path, data):
    try:
        if not os.path.exists(module_path):
            data.setdefault("log", []).append(f"❌ module not found: {module_path}")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)

        if spec is None or spec.loader is None:
            data.setdefault("log", []).append(f"❌ invalid module spec: {module_path}")
            return data, False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "run"):
            data.setdefault("log", []).append("❌ module has no run()")
            return data, False

        result = module.run(data)

        if isinstance(result, dict):
            data = result

        return data, True

    except Exception as e:
        data.setdefault("log", []).append(f"❌ module error: {e}")
        return data, False


# =========================
# 🧩 CREATE MODULE
# =========================
def create_module(data):
    try:
        os.makedirs("modules", exist_ok=True)

        name = f"module_auto_{random.randint(1000, 999999)}"
        path = os.path.join("modules", name + ".py")

        code = f'''
def run(data):
    data.setdefault("log", []).append("⚙️ {name} running")

    goal = data.setdefault("goal", {{}})
    goal["progress"] = goal.get("progress", 0) + 10

    data.setdefault("value", 0)
    data["value"] += 1

    data["log"].append("📈 progress +10")

    return data
'''

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        data["module"] = name
        data.setdefault("log", []).append(f"🧩 created module: {name}")

        return data, True

    except Exception as e:
        data.setdefault("log", []).append(f"❌ create_module error: {e}")
        return data, False


# =========================
# 🚀 EXECUTION CORE (FIXED)
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("execution_result", {})

    decision = data.get("decision")
    module_used = data.get("module")
    success = False

    # =========================
    # 🧩 CREATE MODULE
    # =========================
    if decision == "create_module":
        data, success = create_module(data)
        module_used = data.get("module")

        if success:
            data["log"].append(f"🧠 new module created: {module_used}")
        else:
            data["log"].append("❌ failed to create module")

    # =========================
    # 🚀 RUN MODULE
    # =========================
    elif decision == "run_module" and module_used:
        module_used = module_used.replace(".py", "")
        path = os.path.join("modules", module_used + ".py")

        data, success = run_python_module(path, data)

        if success:
            data["log"].append(f"🚀 executed: {module_used}")
        else:
            data["log"].append(f"❌ failed execution: {module_used}")

    else:
        data["log"].append("⚠️ execution skipped")

    # =========================
    # 🧠 EXPERIENCE (ВАЖНО)
    # =========================
    data["experience"].append({
        "module": module_used,
        "score": data.get("evaluation", {}).get("score", 50)
    })

    # =========================
    # 📦 RESULT
    # =========================
    data["execution_result"] = {
        "module": module_used,
        "success": success
    }

    return data


# alias
def execute(data):
    return execution(data)
