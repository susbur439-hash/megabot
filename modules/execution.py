import os
import importlib.util
import random
import time

from core.system_state import system_state
from modules.control_bus import emit

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
# 📡 EVENT EMITTER (NEW)
# =========================
def emit_event(name, data, extra=None, success=None):

    try:
        emit({
            "event": name,
            "module": data.get("module"),
            "decision": data.get("decision"),
            "success": success,
            "ts": time.time(),
            "extra": extra or {}
        })
    except:
        pass


# =========================
# 📦 MODULE RUNNER
# =========================
def run_python_module(module_path, data, state):

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

        result = module.run(data, state)

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
        os.makedirs(MODULES_DIR, exist_ok=True)

        name = f"module_auto_{random.randint(1000, 999999)}"
        path = os.path.join(MODULES_DIR, name + ".py")

        code = f"""
def run(data, state=None):
    data.setdefault("log", []).append("⚙️ {name} running")

    goal = data.setdefault("goal", {{}})
    goal["progress"] = goal.get("progress", 0) + 10

    data.setdefault("value", 0)
    data["value"] += 1

    data["log"].append("📈 progress +10")

    return data
"""

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        data["module"] = name
        data.setdefault("log", []).append(f"🧩 created module: {name}")

        return data, True

    except Exception as e:
        data.setdefault("log", []).append(f"❌ create_module error: {e}")
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

        if avg < DELETE_THRESHOLD and global_block and os.path.exists(path):
            try:
                os.remove(path)
                data.setdefault("log", []).append(
                    f"🗑️ deleted module: {module} (avg={round(avg,1)})"
                )
            except Exception as e:
                data.setdefault("log", []).append(f"❌ delete failed: {module} | {e}")


# =========================
# 🚀 EXECUTION CORE (EVENT GRAPH ENABLED)
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("execution_result", {})

    # =========================
    # 🧠 STATE
    # =========================
    state = system_state.load()
    state = system_state.inject(data)

    decision = data.get("decision")
    module_used = data.get("module")
    success = False

    emit_event("execution.start", data)

    # =========================
    # 🧩 CREATE
    # =========================
    if decision == "create_module":

        emit_event("create.start", data)

        data, success = create_module(data)
        module_used = data.get("module")

        emit_event("create.end", data, success=success)

    # =========================
    # 🚀 RUN
    # =========================
    elif decision == "run_module" and module_used:

        emit_event("run.start", data)

        module_used = str(module_used).replace(".py", "").replace("modules/", "")
        path = os.path.join(MODULES_DIR, module_used + ".py")

        data, success = run_python_module(path, data, state)

        emit_event("run.end", data, success=success)

    else:
        data.setdefault("log", []).append("⚠️ execution skipped")
        emit_event("execution.skipped", data)

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
    # 🧠 STATE UPDATE
    # =========================
    state["last_module"] = module_used
    state["last_success"] = success
    state["cycle"] = state.get("cycle", 0) + 1

    system_state.state = state

    # =========================
    # 🧹 CLEANUP
    # =========================
    try:
        cleanup_modules(data)
    except Exception as e:
        data.setdefault("log", []).append(f"❌ cleanup error: {e}")

    # =========================
    # 📦 RESULT
    # =========================
    data["execution_result"] = {
        "module": module_used,
        "success": success
    }

    emit_event("execution.end", data, success=success)

    data.setdefault("log", []).append(
        "🧠 learning signal: success" if success else "🧠 learning signal: failure"
    )

    return data


def execute(data):
    return execution(data)