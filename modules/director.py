from modules.task_core import extract_task, normalize_task
from modules.run import run_task


def run(data):
    data.setdefault("log", [])

    # 🧠 TASK NORMALIZE
    task = extract_task(data)
    task = normalize_task(task)
    data["task"] = task

    data["log"].append("🎬 DIRECTOR START")

    # 🚀 передача в ядро
    data = run_task(data)

    data["log"].append("🎬 DIRECTOR END")

    return data
