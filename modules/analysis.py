def analysis(data):
    task = data["task"]

    if "развивай" in task:
        data["analysis"] = "self_development"
    else:
        data["analysis"] = "unknown"

    data["log"].append("analysis done")
    return data
