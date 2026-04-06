def analysis(data):
    task = data["task"]
    memory = data.get("memory", [])
    experience = data.get("experience", [])  # 🔥 ДОБАВИЛИ

    add_module_count = memory.count("add_module")
    run_count = memory.count("run_module")

    # 🔥 последние действия (анализ поведения)
    recent_actions = memory[-3:] if len(memory) >= 3 else memory
    repeated_runs = recent_actions.count("run_module") >= 3

    # 🔥 проверка: есть ли сильный модуль
    best_score = 0
    for exp in experience:
        if isinstance(exp, dict):
            score = exp.get("score", 0)
            if score > best_score:
                best_score = score

    has_strong_module = best_score >= 70

    # 🧠 ОЦЕНКА
    last_result = data.get("result")

    evaluation = {
        "result": "neutral",
        "reason": "",
        "score": 50
    }

    if last_result is None:
        evaluation = {
            "result": "neutral",
            "reason": "first run",
            "score": 60
        }

    elif last_result == "module created":
        evaluation = {
            "result": "good",
            "reason": "created new module",
            "score": 80
        }

    elif last_result == "module improved":
        evaluation = {
            "result": "good",
            "reason": "module improved",
            "score": 70
        }

    elif last_result == "module executed":
        evaluation = {
            "result": "good",
            "reason": "module executed",
            "score": 85
        }

    elif last_result == "alternative created":
        evaluation = {
            "result": "good",
            "reason": "new path created",
            "score": 75
        }

    elif last_result == "module already exists":
        evaluation = {
            "result": "neutral",
            "reason": "no progress",
            "score": 40
        }

    elif last_result == "no action":
        evaluation = {
            "result": "bad",
            "reason": "system stuck",
            "score": 20
        }

    data["evaluation"] = evaluation

    # 🧠 ЛОГИКА (УСИЛЕННАЯ)
    if "развивай" in task:

        # 🔥 1. старт — строим систему
        if add_module_count < 3:
            data["analysis"] = "self_development"

        # 🔥 2. если плохо → меняем стратегию
        elif evaluation["score"] < 30:
            data["analysis"] = "change_strategy"

        # 🔥 3. если есть сильное решение → используем
        elif has_strong_module and not repeated_runs:
            data["analysis"] = "exploit"

        # 🔥 4. если ещё не запускали → меняем стратегию
        elif run_count < 1:
            data["analysis"] = "change_strategy"

        # 🔥 5. если застряли → исследуем
        elif repeated_runs:
            data["analysis"] = "explore"

        # 🔥 6. нормальное исследование
        else:
            data["analysis"] = "explore"

    else:
        data["analysis"] = "unknown"

    data["log"].append(
        f"analysis done (score: {evaluation['score']}, reason: {evaluation['reason']}, recent: {recent_actions}, best_score: {best_score})"
    )

    return data
