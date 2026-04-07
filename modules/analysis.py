def analysis(data):
    task = str(data.get("task", "")).lower()
    memory = data.get("memory", []) or []
    experience = data.get("experience", []) or []
    goal = data.get("goal", {"progress": 0}) or {"progress": 0}

    data.setdefault("log", [])

    # =========================
    # 🧠 TASK TYPE
    # =========================
    if any(w in task for w in ["развивай", "улучшай", "создавай"]):
        task_type = "development"
    elif any(w in task for w in ["исправь", "ошибка", "fix"]):
        task_type = "fix"
    elif any(w in task for w in ["анализ", "определи"]):
        task_type = "analysis"
    else:
        task_type = "unknown"

    data["task_type"] = task_type

    # =========================
    # 📊 RECENT
    # =========================
    recent = memory[-5:]
    repeated_runs = recent.count("run_module") >= 3
    repeated_nothing = recent.count("do_nothing") >= 2

    # =========================
    # 🧠 EXPERIENCE
    # =========================
    module_stats = {}
    scores = []

    for exp in experience:
        if not isinstance(exp, dict):
            continue

        m = exp.get("module")
        s = exp.get("score", 0)

        if isinstance(s, (int, float)):
            scores.append(s)

        if m and isinstance(s, (int, float)):
            module_stats.setdefault(m, []).append(s)

    best_module = None
    best_score = 0

    for m, sc in module_stats.items():
        if sc:
            avg = sum(sc) / len(sc)

            if len(sc) < 2:
                avg *= 0.9

            if avg > best_score:
                best_score = avg
                best_module = m

    has_any_module = len(module_stats) > 0
    has_strong_module = best_score >= 75

    # =========================
    # 📈 TREND
    # =========================
    trend = "stable"
    stagnation = False

    if len(scores) >= 3:
        last3 = scores[-3:]

        if last3[2] > last3[1] >= last3[0]:
            trend = "up"
        elif last3[2] < last3[1] <= last3[0]:
            trend = "down"
        else:
            if max(last3) - min(last3) <= 5:
                stagnation = True

    data["local_trend"] = trend

    # =========================
    # 🔥 РЕАЛЬНЫЙ DELTA (ФИКС)
    # =========================
    prev_progress = data.get("prev_progress", goal.get("progress", 0))
    current_progress = goal.get("progress", 0)

    last_delta = current_progress - prev_progress
    data["last_delta"] = last_delta
    data["prev_progress"] = current_progress

    # =========================
    # 🧠 ОЦЕНКА
    # =========================
    is_first_run = len(memory) == 0

    if is_first_run:
        score = 60
        reason = "first run"

    elif last_delta >= 15:
        score = 95
        reason = "high improvement"

    elif last_delta >= 10:
        score = 90
        reason = "strong improvement"

    elif last_delta > 0:
        score = 75
        reason = "progress"

    elif last_delta == 0:
        score = 45
        reason = "no progress"

    else:
        score = 15
        reason = "regression"

    evaluation = {
        "result": "good" if score >= 70 else "neutral" if score >= 45 else "bad",
        "score": score,
        "reason": reason,
        "delta": last_delta
    }

    data["evaluation"] = evaluation

    # =========================
    # 🧠 BEHAVIOR
    # =========================
    if trend == "down":
        behavior = "aggressive"
    elif stagnation:
        behavior = "explore"
    elif trend == "up":
        behavior = "exploit"
    else:
        behavior = "balanced"

    data["behavior"] = behavior

    # =========================
    # 🔥 MODE
    # =========================
    progress = goal.get("progress", 0)

    if repeated_nothing or score < 20:
        mode = "recovery"

    elif repeated_runs:
        mode = "optimize"

    elif not has_any_module:
        mode = "bootstrap"

    elif task_type == "fix":
        mode = "improve"

    elif task_type == "development":
        if behavior in ["aggressive", "explore"]:
            mode = "explore"
        elif behavior == "exploit":
            mode = "exploit"
        elif progress > 85:
            mode = "optimize"
        else:
            mode = "build"

    elif task_type == "analysis":
        if not has_any_module:
            mode = "build"
        elif not has_strong_module:
            mode = "explore"
        else:
            mode = "exploit"

    else:
        mode = "explore" if score >= 50 else "improve"

    data["analysis"] = mode

    # =========================
    # 📘 LOG
    # =========================
    best_str = f"{best_module}({round(best_score,1)})" if best_module else "None"

    data["log"].append(
        f"analysis: {mode} | behavior: {behavior} | trend: {trend} | stagnation: {stagnation} | score: {score} | delta: {last_delta} | best: {best_str}"
    )

    return data
