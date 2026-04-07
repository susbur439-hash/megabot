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
    recent_actions = memory[-5:]
    repeated_runs = recent_actions.count("run_module") >= 3
    repeated_nothing = recent_actions.count("do_nothing") >= 2

    # =========================
    # 🧠 ОПЫТ
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

    # лучший модуль
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
    # 📈 TREND + STAGNATION
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
    # 🧠 ОЦЕНКА (УЛУЧШЕННАЯ)
    # =========================
    last_result = str(data.get("result", ""))

    score = 50

    if "executed" in last_result:
        score = 85
    elif "tested" in last_result:
        score = 70
    elif "improved" in last_result:
        score = 75
    elif "idea" in last_result:
        score = 60
    elif "no action" in last_result:
        score = 10

    # 🔥 если есть числовой результат — усиливаем
    import re
    numbers = re.findall(r"\d+", last_result)
    if numbers:
        score = int(numbers[-1])

    evaluation = {
        "result": "auto",
        "score": max(0, min(100, score))
    }

    data["evaluation"] = evaluation

    # =========================
    # 🎯 ПРОГРЕСС
    # =========================
    progress = goal.get("progress", 0)

    # =========================
    # 🧠 ПОВЕДЕНИЕ
    # =========================
    if trend == "down" or stagnation:
        behavior = "aggressive"
    elif trend == "up":
        behavior = "exploit"
    else:
        behavior = "balanced"

    data["behavior"] = behavior

    # =========================
    # 🔥 ГЛАВНАЯ ЛОГИКА
    # =========================

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
    # 📘 ЛОГ
    # =========================
    data["log"].append(
        f"analysis: {mode} | behavior: {behavior} | trend: {trend} | stagnation: {stagnation} | score: {evaluation['score']} | best: {best_module}({best_score})"
    )

    return data
