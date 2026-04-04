def action(data):
    if data["decision"] == "add_module":
        data["result"] = "System wants to add a new module"
    else:
        data["result"] = "No action"

    data["log"].append("action selected")
    return data
