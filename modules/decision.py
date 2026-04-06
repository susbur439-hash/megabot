def decision(data):
    memory = data.get("memory", [])
    evaluation = data.get("evaluation", {})
    goal = data.get("goal", {})
    experience = data.get("experience", [])  # 🔥 ДОБАВИЛИ

    score = evaluation.get("score", 50)
    progress = goal.get("progress", 0)

    # 🔥 НАХОДИМ ЛУЧШИЙ МОДУЛЬ
    best_module = None
    best_score = 0

    for exp in experience:
        if exp["score"] > best_score:
            best_score = exp["score"]
            best_module = exp["module"]

    if data["analysis"] == "self_development":
        data["decision"] = "add_module"
        data["result"] = "System wants to add a new module"

    elif data["analysis"] == "change_strategy":
        improve_count = memory.count("improve_module")
        run_count = memory.count("run_module")

        # 🔥 1. ЕСЛИ ПЛОХО → СМЕНА
        if score < 30:
            data["decision"] = "create_alternative"
            data["result"] = "System escapes bad path"

        # 🔥 2. ЕСЛИ МАЛО ОПЫТА → ИССЛЕДУЕМ
        elif len(experience) < 3:
            data["decision"] = "create_alternative"
            data["result"] = "System gathers experience"

        # 🛠 3. УЛУЧШАЕМ
        elif improve_count < 2:
            data["decision"] = "improve_module"
            data["result"] = "System improves module"

        # 🚀 4. ЗАПУСК
        elif run_count < 1:
            data["decision"] = "run_module"
            data["result"] = "System runs module"

        # 🔥 5. ИСПОЛЬЗУЕМ ЛУЧШЕЕ
        elif best_module:
            data["decision"] = "run_module"
            data["result"] = f"Using best module: {best_module} ({best_score})"

        else:
            data["decision"] = "create_alternative"
            data["result"] = "Fallback explore"

    elif data["analysis"] == "explore":
        # 🔥 ВАЖНО — теперь используем опыт
        if best_module and best_score > 60:
            data["decision"] = "run_module"
            data["result"] = f"Exploit best module: {best_module}"
        else:
            data["decision"] = "create_alternative"
            data["result"] = "Exploring new path"

    else:
        data["decision"] = "do_nothing"
        data["result"] = "No action"

    data["log"].append(
        f"decision made (score: {score}, progress: {progress}, best: {best_module})"
    )

    return data
