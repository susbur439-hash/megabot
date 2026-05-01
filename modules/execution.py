import os
import json
import importlib.util


def run_python_module(module_path, data):
    try:
        if not os.path.exists(module_path):
            data.setdefault("log", []).append(f"❌ module not found: {module_path}")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
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


def execution(data):

    data.setdefault("log", [])
    data.setdefault("experience", [])

    module_used = data.get("module")

    result_data = data
    success = False

    # 🚀 only execution
    if module_used:
        path = os.path.join("modules", module_used + ".py")
        result_data, success = run_python_module(path, data)

        if success:
            result_data["log"].append(f"🚀 executed: {module_used}")

    # 📦 ONLY RESULT (NO LEARNING HERE)
    result_data["execution_result"] = {
        "module": module_used,
        "success": success
    }

    return result_data


def execute(data):
    return execution(data)
