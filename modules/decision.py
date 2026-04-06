def decision(data):
    memory = data.get("memory", [])
    evaluation = data.get("evaluation", {})

    score = evaluation.get("score", 50)

    if data["analysis"] == "self_development":
        data["decision"] = "add_module"
        data["result"] = "System wants to add a new module"

    elif data["analysis"] == "change_strategy":
        improve_count = memory.count("improve_module")
        run_count = memory.count("run_module")

        # 🔥 1. если очень плохо → сразу смена
        if score < 30:
            data["decision"] = "create_alternative"
            data["result"] = "System escapes bad path"

        # 🛠 2. если нормально → улучшаем
        elif improve_count < 2:
            data["decision"] = "improve_module"
            data["result"] = "System improves module"

        # 🚀 3. потом запускаем
        elif run_count < 1:
            data["decision"] = "run_module"
            data["result"] = "System runs module"

        # 🔄 4. потом ищем альтернативу
        else:
            data["decision"] = "create_alternative"
            data["result"] = "System explores alternative"

    elif data["analysis"] == "explore":
        data["decision"] = "create_alternative"
        data["result"] = "System explores new path"

    else:
        data["decision"] = "do_nothing"
        data["result"] = "No action"

    data["log"].append(f"decision made (score: {score})")
    return data
