from modules.task_core import extract_task, normalize_task
from modules.run import run_task
from modules.decision import decide
from modules.evaluation import run as evaluate
from modules.learning_writer import learn   # 🔥 learning layer


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
        # 🧠 DECISION
        # =========================
        decision_data = decide(data)

        action = decision_data.get("decision")
        module = decision_data.get("module")

        data["decision"] = action
        data["module"] = module

        data["log"].append(
            f"🧠 DECISION: {action} | module: {module}"
        )

        # =========================
        # 🧨 ANTI-LOOP PROTECTION
        # =========================
        if action == "create_module":
            data["create_count"] = data.get("create_count", 0) + 1

            if data["create_count"] >= 3:
                if data.get("experience"):
                    best = max(data["experience"], key=lambda x: x.get("score", 0))
                    data["module"] = best.get("module")
                    data["decision"] = "run_module"
                    data["log"].append("🧠 ANTI-LOOP → forced run_module")
        else:
            data["create_count"] = 0

        # =========================
        # 🚀 EXECUTION
        # =========================
        result = run_task(data)

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

        data["evaluation"] = eval_result
        score = eval_result.get("score", 0)

        # =========================
        # 🧠 LEARNING (SAFE HOOK)
        # =========================
        try:
            data = learn(data)
        except Exception as e:
            data["log"].append(f"❌ LEARNING ERROR: {e}")

        # =========================
        # 💾 EXPERIENCE UPDATE (NO DUPLICATES)
        # =========================
        if data.get("module"):
            if (
                not data["experience"]
                or data["experience"][-1].get("module") != data["module"]
            ):
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
