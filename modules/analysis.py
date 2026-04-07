def analysis(data):
    task = data.get("task", "").lower()
    memory = data.get("memory", [])
    experience = data.get("experience", [])
    goal = data.get("goal", {"progress": 0})

    data.setdefault("log", [])

    # =========================
    # 🧠 TASK TYPE
    # =========================
    if any(w in task for w in ["развивай", "улучшай", "создавай"]):
        task_type = "development"
    elif any(w in task for w in ["исправь", "ошибка", "fix"]):
        task_type = "fix"
    elif any(w in task for w in ["анализ", "определи"]):
        task_type = "analysis"
    else:
        task_type = "unknown"

    data["task_type"] = task_type

    # =========================
    # 📊 RECENT
    # =========================
    recent = memory[-5:]
    repeated_runs = recent.count("run_module") >= 3
    repeated_nothing = recent.count("do_nothing") >= 2

    # =========================
    # 🧠 EXPERIENCE
    # =========================
    module_stats = {}
    scores = []

    for exp in experience:
        if isinstance(exp, dict):
            m = exp.get("module")
            s = exp.get("score", 0)

            if m:
                module_stats.setdefault(m, []).append(s)

            scores.append(s)

    best_module = None
    best_score = 0

    for m, sc in module_stats.items():
        avg = sum(sc) / len(sc)
        if avg > best_score:
            best_score = avg
            best_module = m

    has_any_module = len(module_stats) > 0
    has_strong_module = best_score >= 75

    # =========================
    # 📈 TREND
    # =========================
    trend = "stable"
    stagnation = False

    if len(scores) >= 3:
        if scores[-1] > scores[-2] > scores[-3]:
            trend = "up"
        elif scores[-1] < scores[-2] < scores[-3]:
            trend = "down"
        else:
            stagnation = True

    data["trend"] = trend

    # =========================
    # 🧠 НАСТОЯЩАЯ ОЦЕНКА
    # =========================
    last_result = str(data.get("result", ""))
    last_delta = data.get("last_delta", 0)   # 🔥 теперь используем реальный результат
    success = data.get("success", False)

    if not last_result:
        score = 60
        reason = "first run"

    elif not success:
        score = 20
        reason = "execution failed"

    elif last_delta > 10:
        score = 90
        reason = "strong improvement"

    elif last_delta > 0:
        score = 70
        reason = "positive result"

    elif last_delta == 0:
        score = 40
        reason = "no progress"

    else:
        score = 10
        reason = "regression"

    evaluation = {
        "result": "good" if score >= 70 else "neutral" if score >= 40 else "bad",
        "score": score,
        "reason": reason
    }

    data["evaluation"] = evaluation

    # =========================
    # 🧠 BEHAVIOR
    # =========================
    if trend == "down" or stagnation:
        behavior = "aggressive"
    elif trend == "up":
        behavior = "exploit"
    else:
        behavior = "balanced"

    data["behavior"] = behavior

    # =========================
    # 🔥 DECISION MODE
    # =========================
    progress = goal.get("progress", 0)

    if repeated_nothing or evaluation["score"] < 20:
        mode = "recovery"

    elif not has_any_module:
        mode = "bootstrap"

    elif task_type == "fix":
        mode = "improve"

    elif task_type == "development":

        if behavior == "aggressive":
            mode = "explore"

        elif behavior == "exploit":
            mode = "exploit"

        elif progress > 85:
            mode = "optimize"

        else:
            mode = "build"

    elif task_type == "analysis":

        if not has_any_module:
            mode = "build"
        elif not has_strong_module:
            mode = "explore"
        else:
            mode = "exploit"

    else:
        if evaluation["score"] < 50:
            mode = "improve"
        else:
            mode = "explore"

    data["analysis"] = mode

    # =========================
    # 📘 LOG
    # =========================
    data["log"].append(
        f"analysis: {mode} | behavior: {behavior} | trend: {trend} | stagnation: {stagnation} | score: {score} | reason: {reason} | best: {best_module}({best_score})"
    )

    return data
