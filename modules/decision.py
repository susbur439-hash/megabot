def decision(data):
    if data["analysis"] == "self_development":
        data["decision"] = "add_module"
    else:
        data["decision"] = "do_nothing"

    data["log"].append("decision made")
    return data
