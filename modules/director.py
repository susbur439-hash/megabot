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
    data.setdefault("evaluation", {})

    try:
        data["log"].append("🎬 DIRECTOR START")

        # =========================
        # 🧠 TASK PREPROCESS
        # =========================
        try:
            task = extract_task(data)
        except Exception:
            task = data.get("task", "")

        try:
            task = normalize_task(task)
        except Exception:
            pass

        data["task"] = task

        # =========================
        # 🧠 DECISION (ОДИН РАЗ)
        # =========================
        decision_data = decide(data)

        # НЕ ПЕРЕЗАТИРАЕМ ВСЮ DATA
        data["decision"] = decision_data.get("decision")
        data["module"] = decision_data.get("module")

        data["log"].append(
            f"🧠 DECISION: {data['decision']} | module: {data['module']}"
        )

        # =========================
        # 🚀 EXECUTION (ТОЛЬКО ОДИН ПУСК)
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
        # 📊 EVALUATION
        # =========================
        eval_result = evaluate(data)

        if not isinstance(eval_result, dict):
            eval_result = {"score": 0, "delta": -50, "result": "error"}

        score = eval_result.get("score", 0)

        data["evaluation"] = eval_result

        # =========================
        # 💾 EXPERIENCE FIX
        # =========================
        if data.get("module") and score is not None:
            if not data["experience"] or data["experience"][-1].get("module") != data["module"]:
                data["experience"].append({
                    "module": data["module"],
                    "score": score
                })

        # =========================
        # 📊 LOG
        # =========================
        data["log"].append(f"📊 SCORE: {score}")
        data["log"].append("🎬 DIRECTOR END")

        return data

    except Exception as e:
        import traceback

        data["status"] = "error"
        data["error"] = str(e)
        data["trace"] = traceback.format_exc()

        data["log"].append(f"❌ DIRECTOR ERROR: {e}")

        return data
