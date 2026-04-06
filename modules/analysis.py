def analysis(data):
    task = data.get("task", "")
    memory = data.get("memory", [])
    experience = data.get("experience", [])
    goal = data.get("goal", {"progress": 0})

    data.setdefault("log", [])

    # 📊 базовая статистика
    add_module_count = memory.count("add_module")
    run_count = memory.count("run_module")
    improve_count = memory.count("improve_module")

    recent_actions = memory[-5:] if len(memory) >= 5 else memory
    repeated_runs = recent_actions.count("run_module") >= 3
    repeated_nothing = recent_actions.count("do_nothing") >= 2

    # 🧠 анализ опыта
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

    # 🧠 оценка результата
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

    elif last_result == "idea converted to module":
        evaluation = {"result": "good", "reason": "idea became module", "score": 82}

    elif last_result == "no module to run":
        evaluation = {"result": "bad", "reason": "no modules", "score": 25}

    elif last_result == "no action":
        evaluation = {"result": "bad", "reason": "stuck", "score": 15}

    elif last_result == "module limit reached":
        evaluation = {"result": "neutral", "reason": "limit reached", "score": 40}

    data["evaluation"] = evaluation

    # 🎯 ПРОГРЕСС ЦЕЛИ
    progress = goal.get("progress", 0)

    # 🔥 ГЛАВНЫЙ МОЗГ (решение состояния)
    if "развивай" in task or "определи" in task:

        # 1. ❌ система сломалась
        if repeated_nothing or evaluation["score"] < 20:
            data["analysis"] = "recovery"

        # 2. 🧱 нет модулей — строим базу
        elif not has_any_module:
            data["analysis"] = "bootstrap"

        # 3. 🧪 мало модулей — создаём
        elif add_module_count < 5:
            data["analysis"] = "build"

        # 4. 🔥 есть сильный — используем
        elif has_strong_module and not repeated_runs:
            data["analysis"] = "exploit"

        # 5. 🛠 слабый результат — улучшаем
        elif evaluation["score"] < 60:
            data["analysis"] = "improve"

        # 6. 🔁 зациклились — исследуем
        elif repeated_runs:
            data["analysis"] = "explore"

        # 7. 🧠 высокий прогресс — оптимизируем
        elif progress > 70:
            data["analysis"] = "optimize"

        # 8. 💡 нормальное развитие
        else:
            data["analysis"] = "explore"

    else:
        data["analysis"] = "unknown"

    # 📘 лог
    data["log"].append(
        f"analysis: {data['analysis']} | score: {evaluation['score']} | best: {best_module}({best_score}) | recent: {recent_actions}"
    )

    return data
