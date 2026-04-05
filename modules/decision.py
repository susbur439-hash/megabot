def decision(data):
    if data["analysis"] == "self_development":
        data["decision"] = "add_module"
        data["result"] = "System wants to add a new module"

    elif data["analysis"] == "change_strategy":
        data["decision"] = "change_strategy"
        data["result"] = "System changes strategy"

    else:
        data["decision"] = "do_nothing"
        data["result"] = "No action"

    data["log"].append("decision made")
    return data
