def decision(data):
    memory = data.get("memory", [])
    evaluation = data.get("evaluation", {})
    goal = data.get("goal", {})  # 🔥 ДОБАВИЛИ

    score = evaluation.get("score", 50)
    progress = goal.get("progress", 0)  # 🔥 ДОБАВИЛИ

    if data["analysis"] == "self_development":
        data["decision"] = "add_module"
        data["result"] = "System wants to add a new module"

    elif data["analysis"] == "change_strategy":
        improve_count = memory.count("improve_module")
        run_count = memory.count("run_module")

        # 🔥 0. ЕСЛИ ПЛОХО → СБРОС
        if score < 30:
            data["decision"] = "create_alternative"
            data["result"] = "System escapes bad path"

        # 🔥 1. ЕСЛИ ПРОГРЕСС МАЛЕНЬКИЙ → БОЛЬШЕ ИССЛЕДОВАНИЯ
        elif progress < 30:
            data["decision"] = "create_alternative"
            data["result"] = "System explores (low progress)"

        # 🛠 2. СРЕДНИЙ ПРОГРЕСС → УЛУЧШАЕМ
        elif improve_count < 2:
            data["decision"] = "improve_module"
            data["result"] = "System improves module"

        # 🚀 3. ПОТОМ ЗАПУСКАЕМ
        elif run_count < 1:
            data["decision"] = "run_module"
            data["result"] = "System runs module"

        # 🔄 4. АЛЬТЕРНАТИВА
        else:
            data["decision"] = "create_alternative"
            data["result"] = "System explores alternative"

    elif data["analysis"] == "explore":
        # 🔥 учитываем прогресс
        if progress < 50:
            data["decision"] = "create_alternative"
            data["result"] = "System explores new path"
        else:
            data["decision"] = "improve_module"
            data["result"] = "System refines current path"

    else:
        data["decision"] = "do_nothing"
        data["result"] = "No action"

    data["log"].append(
        f"decision made (score: {score}, progress: {progress})"
    )

    return data
