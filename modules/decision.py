def decide(data):
    return decision(data)


def decision(data):

    if not isinstance(data, dict):
        data = {}

    memory = data.get("memory") or []
    evaluation = data.get("evaluation") or {}
    goal = data.get("goal") or {}
    experience = data.get("experience") or []

    if not isinstance(memory, list):
        memory = []

    if not isinstance(experience, list):
        experience = []

    data.setdefault("log", [])

    score = evaluation.get("score", 50)
    progress = goal.get("progress", 0)

    # =========================
    # 🧠 EXPERIENCE ANALYSIS
    # =========================
    module_scores = {}

    for exp in experience:
        if not isinstance(exp, dict):
            continue

        m = exp.get("module")
        s = exp.get("score", 0)

        if m and isinstance(s, (int, float)):
            module_scores.setdefault(m, []).append(s)

    best_module = None
    best_score = 0

    for m, scores in module_scores.items():
        if not scores:
            continue

        avg = sum(scores) / len(scores)

        if len(scores) < 3:
            avg *= 0.8

        if avg > best_score:
            best_score = avg
            best_module = m

    has_strong_module = best_score >= 65

    # =========================
    # 🧠 MODE (ЖЁСТКАЯ ЛОГИКА)
    # =========================
    if score < 45:
        mode = "explore"

    elif score > 75 and has_strong_module:
        mode = "exploit"

    else:
        mode = "balanced"

    # =========================
    # 🔥 DECISION
    # =========================
    if mode == "explore":
        action = "create_module" if not has_strong_module else "run_module"

    elif mode == "exploit":
        action = "run_module" if has_strong_module else "improve_module"

    else:
        action = "run_module" if has_strong_module else "create_module"

    # =========================
    # 💾 OUTPUT
    # =========================
    data["decision"] = action

    data["log"].append(
        f"decision: {action} | mode: {mode} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
