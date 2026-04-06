def analysis(data):
    task = data["task"]
    memory = data.get("memory", [])

    add_module_count = memory.count("add_module")
    run_count = memory.count("run_module")

    # 🧠 ОЦЕНКА
    last_result = data.get("result")

    evaluation = {
        "result": "neutral",
        "reason": "",
        "score": 50
    }

    if last_result == "module created":
        evaluation = {
            "result": "good",
            "reason": "created new module",
            "score": 80
        }

    elif last_result == "module improved":
        evaluation = {
            "result": "good",
            "reason": "module improved",
            "score": 70
        }

    elif last_result == "module executed":
        evaluation = {
            "result": "good",
            "reason": "module executed",
            "score": 85
        }

    elif last_result == "alternative created":
        evaluation = {
            "result": "good",
            "reason": "new path created",
            "score": 75
        }

    elif last_result == "module already exists":
        evaluation = {
            "result": "neutral",
            "reason": "no progress",
            "score": 40
        }

    elif last_result == "no action":
        evaluation = {
            "result": "bad",
            "reason": "system stuck",
            "score": 20
        }

    data["evaluation"] = evaluation

    # 🧠 ЛОГИКА
    if "развивай" in task:
        if add_module_count < 3:
            data["analysis"] = "self_development"

        elif evaluation["score"] < 30:
            data["analysis"] = "change_strategy"

        elif run_count < 1:
            data["analysis"] = "change_strategy"

        else:
            data["analysis"] = "explore"

    else:
        data["analysis"] = "unknown"

    data["log"].append(
        f"analysis done (score: {evaluation['score']}, reason: {evaluation['reason']})"
    )

    return data
