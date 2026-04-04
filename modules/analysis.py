def analysis(data):
    task = data["task"]

    memory = data.get("memory", [])

    # считаем, сколько раз уже делали add_module
    add_module_count = memory.count("add_module")

    if "развивай" in task:
        if add_module_count > 2:
            data["analysis"] = "change_strategy"
        else:
            data["analysis"] = "self_development"
    else:
        data["analysis"] = "unknown"

    data["log"].append("analysis done")
    return data
