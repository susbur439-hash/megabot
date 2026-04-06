def decision(data):
    memory = data.get("memory", [])
    evaluation = data.get("evaluation")

    if data["analysis"] == "self_development":
        data["decision"] = "add_module"
        data["result"] = "System wants to add a new module"

    elif data["analysis"] == "change_strategy":
        improve_count = memory.count("improve_module")
        run_count = memory.count("run_module")

        # 🔥 НОВОЕ: если плохо → сразу меняем стратегию
        if evaluation == "bad":
            data["decision"] = "create_alternative"
            data["result"] = "System switches strategy (bad result)"

        # ✅ если хорошо → продолжаем улучшать
        elif improve_count < 2:
            data["decision"] = "improve_module"
            data["result"] = "System improves module"

        # 🚀 потом запускаем
        elif run_count < 1:
            data["decision"] = "run_module"
            data["result"] = "System runs module"

        # 🔄 потом альтернатива
        else:
            data["decision"] = "create_alternative"
            data["result"] = "System switches to alternative"

    else:
        data["decision"] = "do_nothing"
        data["result"] = "No action"

    data["log"].append("decision made")
    return data
