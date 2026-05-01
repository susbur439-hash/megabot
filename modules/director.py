from modules.task_core import extract_task, normalize_task
from modules.run import run_task


def run(data):
    # 🛡️ Гарантируем структуру
    if not isinstance(data, dict):
        data = {}

    data.setdefault("log", [])

    try:
        # 🧠 TASK PREPROCESS
        task = extract_task(data)
        task = normalize_task(task)
        data["task"] = task

        data["log"].append("🎬 DIRECTOR START")

        # 🚀 CORE EXECUTION
        result = run_task(data)

        # 🛡️ Защита от кривого результата
        if isinstance(result, dict):
            data.update(result)
        else:
            data["result"] = result

        data["log"].append("🎬 DIRECTOR END")

    except Exception as e:
        import traceback
        data["status"] = "error"
        data["error"] = str(e)
        data["trace"] = traceback.format_exc()
        data["log"].append(f"❌ ERROR: {e}")

    return data
