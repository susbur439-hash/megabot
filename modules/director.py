from modules.task_core import extract_task, normalize_task
from modules.run import run_task


def run(data):
    # 🛡️ Полная защита входа
    if not isinstance(data, dict):
        data = {}

    data.setdefault("log", [])

    try:
        data["log"].append("🎬 DIRECTOR START")

        # 🧠 SAFE TASK PREPROCESS
        try:
            task = extract_task(data)
        except Exception:
            task = data.get("task", data)

        try:
            task = normalize_task(task)
        except Exception:
            pass

        data["task"] = task

        # 🚀 EXECUTION
        result = run_task(data)

        # 🛡️ SAFE MERGE RESULT
        if isinstance(result, dict):
            for k, v in result.items():
                # не затираем лог
                if k == "log" and isinstance(v, list):
                    data["log"].extend(v)
                else:
                    data[k] = v
        else:
            data["result"] = result

        data["log"].append("🎬 DIRECTOR END")

        return data

    except Exception as e:
        import traceback

        data["status"] = "error"
        data["error"] = str(e)
        data["trace"] = traceback.format_exc()

        if "log" in data:
            data["log"].append(f"❌ ERROR: {e}")

        return data
