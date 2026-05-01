from modules.task_core import extract_task, normalize_task
from modules.run import run_task
from modules.decision import decide


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

        # 🧠 DECISION LAYER (НОВОЕ)
        try:
            decision = decide(data)
        except Exception as e:
            decision = {"action": "run", "error": str(e)}

        data["decision"] = decision
        data["log"].append(f"🧠 DECISION: {decision}")

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

        data["log"].append(f"❌ DIRECTOR ERROR: {e}")

        return data
