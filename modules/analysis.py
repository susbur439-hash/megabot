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

    # 🧠 НОВОЕ — ОЦЕНКА РЕЗУЛЬТАТА
    last_result = data.get("result")

    if last_result == "no action":
        data["evaluation"] = "bad"
    elif last_result in [
        "module improved",
        "module created",
        "module executed",
        "alternative created"
    ]:
        data["evaluation"] = "good"
    else:
        data["evaluation"] = "neutral"

    data["log"].append(f"analysis done (eval: {data['evaluation']})")
    return data
