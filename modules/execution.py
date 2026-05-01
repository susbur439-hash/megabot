import os
import importlib.util


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

        # ⚡ run module
        result = module.run(data)

        # 🧠 IMPORTANT:
        # allow both styles:
        # 1) return dict
        # 2) mutate in place
        if isinstance(result, dict):
            data = result

        return data, True

    except Exception as e:
        data.setdefault("log", []).append(f"❌ module error: {e}")
        return data, False


# =========================
# 🚀 EXECUTION (PURE RUNNER)
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("execution_result", {})

    module_used = data.get("module")

    success = False

    # =========================
    # 🚀 RUN MODULE
    # =========================
    if module_used:
        module_used = module_used.replace(".py", "")
        path = os.path.join("modules", module_used + ".py")

        data, success = run_python_module(path, data)

        if success:
            data["log"].append(f"🚀 executed: {module_used}")
        else:
            data["log"].append(f"❌ failed execution: {module_used}")

    else:
        data["log"].append("❌ no module provided")

    # =========================
    # 📦 OUTPUT ONLY
    # =========================
    data["execution_result"] = {
        "module": module_used,
        "success": success
    }

    return data


# alias
def execute(data):
    return execution(data)
