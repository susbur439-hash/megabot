def analysis(data):
    task = data.get("task", "").lower()
    memory = data.get("memory", [])
    experience = data.get("experience", [])
    goal = data.get("goal", {"progress": 0})

    data.setdefault("log", [])

    # =========================
    # 🧠 TASK INTERPRETER
    # =========================
    if any(word in task for word in ["развивай", "улучшай", "создавай"]):
        task_type = "development"
    elif any(word in task for word in ["исправь", "ошибка", "fix"]):
        task_type = "fix"
    elif any(word in task for word in ["определи", "анализируй"]):
        task_type = "analysis"
    else:
        task_type = "unknown"

    data["task_type"] = task_type

    # =========================
    # 📊 СТАТИСТИКА
    # =========================
    add_module_count = memory.count("add_module")
    run_count = memory.count("run_module")
    improve_count = memory.count("improve_module")

    recent_actions = memory[-5:] if len(memory) >= 5 else memory

    repeated_runs = recent_actions.count("run_module") >= 3
    repeated_nothing = recent_actions.count("do_nothing") >= 2

    # =========================
    # 🧠 ОПЫТ + ДИНАМИКА
    # =========================
    module_stats = {}
    score_trend = []

    for exp in experience:
        if isinstance(exp, dict):
            m = exp.get("module")
            s = exp.get("score", 0)

            if m:
                module_stats.setdefault(m, []).append(s)

            score_trend.append(s)

    best_module = None
    best_score = 0

    for m, scores in module_stats.items():
        if scores:
            avg = sum(scores) / len(scores)
            if avg > best_score:
                best_score = avg
                best_module = m

    has_strong_module = best_score >= 75
    has_any_module = len(module_stats) > 0

    # 📈 ТРЕНД (очень важно)
    trend = "stable"
    if len(score_trend) >= 3:
        if score_trend[-1] > score_trend[-2] > score_trend[-3]:
            trend = "up"
        elif score_trend[-1] < score_trend[-2] < score_trend[-3]:
            trend = "down"

    data["trend"] = trend

    # =========================
    # 🧠 ОЦЕНКА
    # =========================
    last_result = data.get("result")

    evaluation = {
        "result": "neutral",
        "reason": "",
        "score": 50
    }

    if last_result is None:
        evaluation = {"result": "neutral", "reason": "first run", "score": 60}

    elif "tested" in str(last_result):
        evaluation = {"result": "good", "reason": "module tested", "score": 70}

    elif "executed" in str(last_result):
        evaluation = {"result": "good", "reason": "execution success", "score": 85}

    elif last_result == "idea generated":
        evaluation = {"result": "good", "reason": "thinking", "score": 65}

    elif last_result == "no action":
        evaluation = {"result": "bad", "reason": "stuck", "score": 15}

    data["evaluation"] = evaluation

    # =========================
    # 🎯 ПРОГРЕСС
    # =========================
    progress = goal.get("progress", 0)

    # =========================
    # 🧠 РЕЖИМ ПОВЕДЕНИЯ (NEW 🔥)
    # =========================
    if trend == "down":
        behavior = "aggressive"   # ломаем старое, ищем новое
    elif trend == "up":
        behavior = "exploit"      # усиливаем лучшее
    else:
        behavior = "balanced"     # стандарт

    data["behavior"] = behavior

    # =========================
    # 🔥 ГЛАВНАЯ ЛОГИКА
    # =========================

    # 🚨 1. ВЫХОД ИЗ ТУПИКА
    if repeated_nothing or evaluation["score"] < 20:
        data["analysis"] = "recovery"

    # 🧱 2. СТАРТ
    elif not has_any_module:
        data["analysis"] = "bootstrap"

    # 🔧 3. FIX
    elif task_type == "fix":
        data["analysis"] = "improve"

    # 🚀 4. DEVELOPMENT
    elif task_type == "development":

        if behavior == "aggressive":
            data["analysis"] = "explore"

        elif behavior == "exploit":
            data["analysis"] = "exploit"

        elif add_module_count < 5:
            data["analysis"] = "build"

        elif progress > 80:
            data["analysis"] = "optimize"

        else:
            data["analysis"] = "explore"

    # 🧠 5. ANALYSIS
    elif task_type == "analysis":

        if not has_any_module:
            data["analysis"] = "build"
        elif not has_strong_module:
            data["analysis"] = "explore"
        else:
            data["analysis"] = "exploit"

    # ❓ 6. FALLBACK
    else:
        if not has_any_module:
            data["analysis"] = "bootstrap"
        elif evaluation["score"] < 50:
            data["analysis"] = "improve"
        else:
            data["analysis"] = "explore"

    # =========================
    # 📘 ЛОГ
    # =========================
    data["log"].append(
        f"analysis: {data['analysis']} | behavior: {behavior} | trend: {trend} | score: {evaluation['score']} | best: {best_module}({best_score}) | recent: {recent_actions}"
    )

    return data
