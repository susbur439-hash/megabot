def decision(data):
    memory = data.get("memory", [])

    if data["analysis"] == "self_development":
        data["decision"] = "add_module"
        data["result"] = "System wants to add a new module"

    elif data["analysis"] == "change_strategy":
        # 🧠 умная смена стратегии
        improve_count = memory.count("improve_module")

        if improve_count < 2:
            data["decision"] = "improve_module"
            data["result"] = "System tries to improve module"
        else:
            data["decision"] = "create_alternative"
            data["result"] = "System switches to alternative"

    else:
        data["decision"] = "do_nothing"
        data["result"] = "No action"

    data["log"].append("decision made")
    return data
