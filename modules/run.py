import os
import subprocess

from modules.decision import decide


def safe_import_execute():
    try:
        from modules.execution import execute
        return execute
    except Exception as e:
        print(f"[EXECUTION IMPORT ERROR] {e}")
        return None


# =========================
# 🛡️ DATA TYPE GUARD
# =========================
def normalize_data(data):

    if not isinstance(data, dict):
        data = {"task": str(data)}

    if not isinstance(data.get("log"), list):
        data["log"] = []

    if not isinstance(data.get("experience"), list):
        data["experience"] = []

    if not isinstance(data.get("evaluation"), dict):
        data["evaluation"] = {}

    return data


# =========================
# 🚀 DIRECT PYTHON EXECUTION
# =========================
def run_python_file(task, data):

    try:
        parts = str(task).strip().split()

        if len(parts) != 2:
            return data

        command, filename = parts

        if command != "python":
            return data

        if not filename.endswith(".py"):
            return data

        if not os.path.exists(filename):
            data["log"].append(f"❌ file not found: {filename}")
            return data

        data["log"].append(f"🚀 DIRECT START: {filename}")

        result = subprocess.run(
            ["python", filename],
            capture_output=True,
            text=True
        )

        if result.stdout:
            data["log"].append(result.stdout)

        if result.stderr:
            data["log"].append(result.stderr)

        data["status"] = "ok"

        data["log"].append(f"✅ DIRECT END: {filename}")

        return data

    except Exception as e:

        data["status"] = "error"
        data["error"] = str(e)

        data["log"].append(f"❌ DIRECT EXEC ERROR: {e}")

        return data


# =========================
# 🚀 RUN TASK
# =========================
def run_task(data):

    data = normalize_data(data)

    print(f"[RUN] Выполнение задачи: {data}")

    task = str(data.get("task", "")).strip()

    # =========================
    # 🚀 DIRECT BUILDER MODE
    # =========================
    if task.startswith("python ") and "megabot_controlled_builder.py" in task:

        return run_python_file(task, data)

    # =========================
    # 🧠 DECISION LAYER
    # =========================
    data = decide(data)

    decision = data.get("decision")

    if not decision:
        data["status"] = "error"
        data["error"] = "No decision produced"
        return data

    data["log"].append(f"[RUN] decision -> {decision}")

    # =========================
    # ⚙ EXECUTION LAYER
    # =========================
    execute = safe_import_execute()

    if execute is None:

        data["status"] = "error"
        data["error"] = "execution module not available"

        data["log"].append("❌ execution missing")

        return data

    try:
        result = execute(data)

    except Exception as e:

        data["status"] = "error"
        data["error"] = str(e)

        data["log"].append(f"[RUN ERROR] {e}")

        return data

    # =========================
    # 🧩 SAFE MERGE
    # =========================
    if isinstance(result, dict):

        for k, v in result.items():

            if k == "log" and isinstance(v, list):
                data["log"].extend(v)

            elif k == "experience":
                if isinstance(v, list):
                    data["experience"] = v

            elif k == "evaluation":
                if isinstance(v, dict):
                    data["evaluation"] = v

            else:
                data[k] = v

    # =========================
    # 🛡️ FINAL SAFETY
    # =========================
    data = normalize_data(data)

    data["status"] = data.get("status", "ok")

    return data
