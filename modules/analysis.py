def load_memory():
    try:
        with open("memory.txt", "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []


def analysis(data):
    task = data["task"]

    memory = load_memory()

    # считаем, сколько раз уже делали add_module
    add_module_count = sum("add_module" in line for line in memory)

    if "развивай" in task:
        if add_module_count > 2:
            data["analysis"] = "change_strategy"
        else:
            data["analysis"] = "self_development"
    else:
        data["analysis"] = "unknown"

    data["log"].append("analysis done")
    return data
