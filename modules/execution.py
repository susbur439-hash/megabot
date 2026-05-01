import os
import importlib.util


def run_python_module(module_path, data):
    try:
        if not os.path.exists(module_path):
            data.setdefault("log", []).append(f"❌ module not found: {module_path}")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)

        if spec is None or spec.loader is None:
            return data, False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            result = module.run(data)
            if isinstance(result, dict):
                return result, True

        return data, False

    except Exception as e:
        data.setdefault("log", []).append(f"❌ module error: {e}")
        return data, False


# =========================
# 🚀 EXECUTION CORE (БЕЗ ПУСТОТЫ)
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("execution_result", {})

    module_used = data.get("module")
    success = False

    # =========================
    # 🔥 ALWAYS EXECUTE SOMETHING
    # =========================
    if module_used:
        path = os.path.join("modules", module_used + ".py")

        data, success = run_python_module(path, data)

        if success:
            data["log"].append(f"🚀 executed: {module_used}")
        else:
            data["log"].append(f"❌ failed: {module_used}")

    # =========================
    # 🧨 FALLBACK (КЛЮЧЕВОЕ)
    # =========================
    else:
        fallback = f"auto_{len(os.listdir('modules')) if os.path.exists('modules') else 0}.py"
        path = os.path.join("modules", fallback)

        os.makedirs("modules", exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write("""
def run(data):
    data.setdefault("log", []).append("⚙️ fallback module active")
    data.setdefault("goal", {}).setdefault("progress", 0)
    data["goal"]["progress"] += 5
    return data
""")

        data, success = run_python_module(path, data)

        data["log"].append(f"🧩 fallback created: {fallback}")

    # =========================
    # 📦 RESULT
    # =========================
    data["execution_result"] = {
        "module": module_used,
        "success": success
    }

    return data
