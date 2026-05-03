from modules.task_core import extract_task, normalize_task
from modules.run import run_task
from modules.decision import decide
from modules.evaluation import run as evaluate


def run(data):
    # 🛡️ защита входа
    if not isinstance(data, dict):
        data = {}

    data.setdefault("log", [])
    data.setdefault("experience", [])

    try:
        data["log"].append("🎬 DIRECTOR START")

        # =========================
        # 🧠 TASK PREPROCESS
        # =========================
        try:
            task = extract_task(data)
        except Exception:
            task = data.get("task", data)

        try:
            task = normalize_task(task)
        except Exception:
            pass

        data["task"] = task

        # =========================
        # 🧠 DECISION
        # =========================
        data = decide(data)

        data["log"].append(
            f"🧠 DECISION: {data.get('decision')} | module: {data.get('module')}"
        )

        # =========================
        # 🚀 EXECUTION
        # =========================
        result = run_task(data)

        # =========================
        # 🔗 MERGE RESULT
        # =========================
        if isinstance(result, dict):
            for k, v in result.items():
                if k == "log" and isinstance(v, list):
                    data["log"].extend(v)
                else:
                    data[k] = v
        else:
            data["result"] = result

        # =========================
        # 📊 EVALUATION (FIXED)
        # =========================
        eval_result = evaluate(data)   # ❗ НЕ ПЕРЕЗАТИРАЕМ data

        if isinstance(eval_result, dict):
            data["evaluation"] = eval_result

            # 💾 СОХРАНЯЕМ В ОПЫТ
            if data.get("module"):
                data["experience"].append({
                    "module": data.get("module"),
                    "score": eval_result.get("score", 50)
                })

        data["log"].append(
            f"📊 SCORE: {data.get('evaluation', {}).get('score')}"
        )

        data["log"].append("🎬 DIRECTOR END")

        return data

    except Exception as e:
        import traceback

        data["status"] = "error"
        data["error"] = str(e)
        data["trace"] = traceback.format_exc()

        data["log"].append(f"❌ DIRECTOR ERROR: {e}")

        return data
