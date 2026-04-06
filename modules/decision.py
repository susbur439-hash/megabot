def decision(data):
    if data["analysis"] == "self_development":
        data["decision"] = "add_module"
        data["result"] = "System wants to add a new module"

    elif data["analysis"] == "change_strategy":
        # 🔥 НОВОЕ ПОВЕДЕНИЕ
        if "change_strategy" not in data.get("memory", []):
            data["decision"] = "improve_module"
            data["result"] = "System tries to improve existing module"
        else:
            data["decision"] = "create_alternative"
            data["result"] = "System tries alternative approach"

    else:
        data["decision"] = "do_nothing"
        data["result"] = "No action"

    data["log"].append("decision made")
    return data
