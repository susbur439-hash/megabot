import os
import importlib.util
import random

from core.system_state import system_state

# =========================
# ⚙ CONFIG
# =========================
MODULES_DIR = "modules"
DELETE_THRESHOLD = 30
MIN_RUNS_TO_DELETE = 3

PROTECTED_MODULES = {
    "task_core",
    "decision",
    "control_bus",
    "execution",
    "control_layer",
    "system_observer"
}

# =========================
# 📦 MODULE RUNNER
# =========================
def run_python_module(module_path, data):
    try:
        if not os.path.exists(module_path):
            data["log"].append(f"❌ module not found: {module_path}")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)

        if spec is None or spec.loader is None:
            data["log"].append(f"❌ invalid module spec: {module_path}")
            return data, False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "run"):
            data["log"].append("❌ module has no run()")
            return data, False

        result = module.run(data)

        if isinstance(result, dict):
            data = result

        return data, True

    except Exception as e:
        data["log"].append(f"❌ module error: {e}")
        return data, False


# =========================
# 🧩 CREATE MODULE
# =========================
def create_module(data):
    try:
        os.makedirs(MODULES_DIR, exist_ok=True)

        name = f"module_auto_{random.randint(1000, 999999)}"
        path = os.path.join(MODULES_DIR, name + ".py")

        code = f"""
def run(data):
    data.setdefault("log", []).append("⚙️ {name} running")

    goal = data.setdefault("goal", {{}})
    goal["progress"] += 10 if "progress" in goal else 10

    data.setdefault("value", 0)
    data["value"] += 1

    data["log"].append("📈 progress +10")

    return data
"""

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        data["module"] = name
        data["log"].append(f"🧩 created module: {name}")

        return data, True

    except Exception as e:
        data["log"].append(f"❌ create_module error: {e}")
        return data, False


# =========================
# 🧹 CLEANUP
# =========================
def cleanup_modules(data):

    experience = data.get("experience", [])
    control_flags = data.get("control_flags", {})

    stats = {}

    for e in experience:
        if not isinstance(e, dict):
            continue

        m = e.get("module")
        s = e.get("score")

        if m and s is not None:
            stats.setdefault(m, []).append(s)

    global_block = (
        control_flags.get("overcreate", False)
        or control_flags.get("loop_detected", False)
    )

    for module, scores in stats.items():

        if module in PROTECTED_MODULES:
            continue

        if len(scores) < MIN_RUNS_TO_DELETE:
            continue

        avg = sum(scores) / len(scores)

        path = os.path.join(MODULES_DIR, module + ".py")

        should_delete = avg < DELETE_THRESHOLD and global_block

        if should_delete and os.path.exists(path):
            try:
                os.remove(path)
                data["log"].append(
                    f"🗑️ deleted module: {module} (avg={round(avg,1)})"
                )
            except Exception as e:
                data["log"].append(f"❌ delete failed: {module} | {e}")


# =========================
# 🚀 EXECUTION CORE (STATE-DRIVEN)
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("execution_result", {})

    # =========================
    # 🧠 SYSTEM STATE (LOAD)
    # =========================
    state = system_state.load()
    state = system_state.inject(data, state)

    decision = data.get("decision")
    module_used = data.get("module")
    success = False

    # =========================
    # 🧩 CREATE
    # =========================
    if decision == "create_module":
        data, success = create_module(data)
        module_used = data.get("module")

    # =========================
    # 🚀 RUN
    # =========================
    elif decision == "run_module" and module_used:

        module_used = str(module_used).replace(".py", "").replace("modules/", "")
        path = os.path.join(MODULES_DIR, module_used + ".py")

        data, success = run_python_module(path, data)

    else:
        data["log"].append("⚠️ execution skipped")

    # =========================
    # 🧠 EXPERIENCE
    # =========================
    score = data.get("evaluation", {}).get("score", 50)

    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score,
            "success": success
        })

    # =========================
    # 🧠 UPDATE STATE (КЛЮЧЕВОЕ)
    # =========================
    state["last_module"] = module_used
    state["last_success"] = success
    state["cycle"] = state.get("cycle", 0) + 1

    system_state.save(state)

    # =========================
    # 🧹 CLEANUP
    # =========================
    try:
        cleanup_modules(data)
    except Exception as e:
        data["log"].append(f"❌ cleanup error: {e}")

    # =========================
    # 📦 RESULT
    # =========================
    data["execution_result"] = {
        "module": module_used,
        "success": success
    }

    data["log"].append(
        "🧠 learning signal: success" if success else "🧠 learning signal: failure"
    )

    return data


def execute(data):
    return execution(data)
