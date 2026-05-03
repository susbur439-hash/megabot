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
        # 📊 EVALUATION (ЖЁСТКИЙ ФИКС)
        # =========================
        eval_result = evaluate(data)

        # 🛡️ гарантия структуры
        if not isinstance(eval_result, dict):
            eval_result = {"score": 0, "delta": -50, "result": "error"}

        score = eval_result.get("score", 0)
        delta = eval_result.get("delta", score - 50)

        data["evaluation"] = {
            "score": score,
            "delta": delta,
            "result": eval_result.get("result", "unknown")
        }

        # =========================
        # 💾 EXPERIENCE (ФИКС ДУБЛЕЙ)
        # =========================
        if data.get("module"):
            module_name = data.get("module")

            # не добавляем дубликаты подряд
            if not data["experience"] or data["experience"][-1].get("module") != module_name:
                data["experience"].append({
                    "module": module_name,
                    "score": score
                })

        # =========================
        # 🧠 АНТИ-ЗАЦИКЛИВАНИЕ
        # =========================
        if data.get("decision") == "create_module":
            repeats = data.get("create_repeats", 0) + 1
            data["create_repeats"] = repeats

            if repeats >= 3 and data["experience"]:
                # пробуем лучший модуль вместо создания
                best = max(data["experience"], key=lambda x: x.get("score", 0))
                data["decision"] = "run_module"
                data["module"] = best.get("module
