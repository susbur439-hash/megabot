def analysis(data):
    task = data.get("task", "").lower()
    memory = data.get("memory", [])
    experience = data.get("experience", [])
    goal = data.get("goal", {"progress": 0})

    data.setdefault("log", [])

    # =========================
    # 🧠 TASK INTERPRETER (NEW)
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
    # 🧠 ОПЫТ
    # =========================
    module_stats = {}

    for exp in experience:
        if isinstance(exp, dict):
            m = exp.get("module")
            s = exp.get("score", 0)
            if m:
                module_stats.setdefault(m, []).append(s)

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

    elif last_result == "module created":
        evaluation = {"result": "good", "reason": "created module", "score": 80}

    elif last_result == "module improved":
        evaluation = {"result": "good", "reason": "improved module", "score": 75}

    elif last_result == "module executed":
        evaluation = {"result": "good", "reason": "execution success", "score": 85}

    elif last_result == "alternative created":
        evaluation = {"result": "good", "reason": "new strategy", "score": 78}

    elif last_result == "idea generated":
        evaluation = {"result": "good", "reason": "thinking", "score": 65}

    elif last_result == "idea → module":
        evaluation = {"result": "good", "reason": "idea became module", "score": 82}

    elif last_result == "no module":
        evaluation = {"result": "bad", "reason": "no modules", "score": 25}

    elif last_result == "no action":
        evaluation = {"result": "bad", "reason": "stuck", "score": 15}

    elif last_result == "limit reached":
        evaluation = {"result": "neutral", "reason": "limit reached", "score": 40}

    data["evaluation"] = evaluation

    # =========================
    # 🎯 ПРОГРЕСС
    # =========================
    progress = goal.get("progress", 0)

    # =========================
    # 🔥 ГЛАВНАЯ ЛОГИКА
    # =========================

    # 🚨 1. ВЫХОД ИЗ ТУПИКА (приоритет №1)
    if repeated_nothing or evaluation["score"] < 20:
        data["analysis"] = "recovery"

    # 🧱 2. СТАРТ СИСТЕМЫ
    elif not has_any_module:
        data["analysis"] = "bootstrap"

    # 🔧 3. FIX режим
    elif task_type == "fix":
        data["analysis"] = "improve"

    # 🚀 4. РАЗВИТИЕ
    elif task_type == "development":

        if add_module_count < 5:
            data["analysis"] = "build"

        elif has_strong_module and not repeated_runs:
            data["analysis"] = "exploit"

        elif repeated_runs:
            data["analysis"] = "explore"

        elif progress > 70:
            data["analysis"] = "optimize"

        else:
            data["analysis"] = "explore"

    # 🧠 5. АНАЛИЗ (новый режим)
    elif task_type == "analysis":

        if not has_any_module:
            data["analysis"] = "build"

        elif not has_strong_module:
            data["analysis"] = "explore"

        else:
            data["analysis"] = "exploit"

    # ❓ 6. FALLBACK (ВАЖНО — больше нет тупика)
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
        f"analysis: {data['analysis']} | task_type: {task_type} | score: {evaluation['score']} | best: {best_module}({best_score}) | recent: {recent_actions}"
    )

    return data
