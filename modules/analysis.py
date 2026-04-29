def run(data):
    """
    Analysis:
    оценивает состояние системы и подготавливает режим работы
    """

    data.setdefault("log", [])

    task_struct = data.get("task_struct", {})
    task_type = task_struct.get("type", "general")
    priority = task_struct.get("priority", "normal")

    goal = data.get("goal", {"progress": 0})

    progress = goal.get("progress", 0)
    prev_progress = data.get("prev_progress", progress)

    delta = progress - prev_progress

    data["prev_progress"] = progress
    data["last_delta"] = delta

    # =========================
    # 📊 ПРОСТАЯ ОЦЕНКА
    # =========================
    if delta > 10:
        score = 90
        state = "growing"
    elif delta > 0:
        score = 70
        state = "progress"
    elif delta == 0:
        score = 40
        state = "stagnation"
    else:
        score = 10
        state = "regression"

    data["evaluation"] = {
        "score": score,
        "delta": delta,
        "state": state
    }

    # =========================
    # 🧠 РЕЖИМ (ключевое)
    # =========================
    if priority == "critical":
        mode = "fix"

    elif state == "regression":
        mode = "recovery"

    elif state == "stagnation":
        mode = "explore"

    elif state == "growing":
        mode = "exploit"

    else:
        mode = "balanced"

    # доп логика от типа задачи
    if task_type == "self_improvement":
        mode = "explore"

    if task_type == "fix":
        mode = "fix"

    data["analysis"] = mode
    data["system_state"] = state

    # =========================
    # 📘 LOG
    # =========================
    data["log"].append(
        f"analysis: mode={mode} | state={state} | delta={delta} | score={score}"
    )

    return data
