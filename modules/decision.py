import random


def decision(data):
    memory = data.get("memory", []) or []
    evaluation = data.get("evaluation", {}) or {}
    goal = data.get("goal", {}) or {}
    experience = data.get("experience", []) or []

    data.setdefault("log", [])

    score = evaluation.get("score", 50)
    progress = goal.get("progress", 0)
    analysis_type = data.get("analysis")
    behavior = data.get("behavior", "balanced")
    trend = data.get("local_trend", "stable")

    # =========================
    # 🧠 ОПЫТ
    # =========================
    module_scores = {}

    for exp in experience:
        if not isinstance(exp, dict):
            continue

        m = exp.get("module")
        s = exp.get("score", 0)

        if isinstance(s, (int, float)) and m:
            module_scores.setdefault(m, []).append(s)

    best_module = None
    best_score = 0

    for m, scores in module_scores.items():
        if scores:
            avg = sum(scores) / len(scores)

            if len(scores) < 2:
                avg *= 0.9

            if avg > best_score:
                best_score = avg
                best_module = m

    has_strong_module = best_score >= 70
    has_any_module = len(module_scores) > 0

    # =========================
    # 🚨 BOOTSTRAP (ФИКС)
    # =========================
    if not has_any_module:
        # создаём, но не бесконечно
        if memory.count("create_module") < 2:
            action = "create_module"
        else:
            action = "run_module"

        data["decision"] = action
        data["log"].append(f"decision: {action} | BOOTSTRAP")
        return data

    # =========================
    # 🧠 АНТИ-ЗАЦИКЛИВАНИЕ
    # =========================
    recent = memory[-5:]

    too_many_creates = recent.count("create_module") >= 3
    too_many_runs = recent.count("run_module") >= 3
    too_many_improves = recent.count("improve_module") >= 3

    stagnation = (
        trend == "stable"
        and score < 75
        and (too_many_runs or too_many_improves)
    )

    # =========================
    # 🔥 ОСНОВНАЯ ЛОГИКА
    # =========================

    if analysis_type == "recovery":
        action = "run_module" if has_strong_module else "improve_module"

    elif analysis_type == "bootstrap":
        action = "create_module"

    elif analysis_type == "build":
        action = "run_module" if too_many_creates else "create_module"

    elif analysis_type == "explore":
        if stagnation:
            action = "create_module"
        elif has_strong_module:
            action = "run_module"
        else:
            action = "create_module"

    elif analysis_type == "exploit":
        if has_strong_module:
            if stagnation or too_many_runs:
                action = "improve_module"
            else:
                action = "run_module"
        else:
            action = "create_module"

    elif analysis_type == "improve":
        if has_strong_module:
            action = "run_module" if too_many_improves else "improve_module"
        else:
            action = "create_module"

    elif analysis_type == "optimize":
        action = "run_module" if has_strong_module else "create_module"

    else:
        action = "run_module" if score >= 50 else "improve_module"

    # =========================
    # 🛡 ЖЁСТКИЙ ФИКС (ВАЖНО)
    # =========================

    # нельзя застревать в create
    if too_many_creates and action == "create_module":
        action = "run_module"

    # нельзя застревать в run
    if too_many_runs and action == "run_module":
        action = "improve_module"

    # всегда должен быть прогресс
    if action not in ["create_module", "run_module", "improve_module"]:
        action = "run_module"

    # =========================
    # 💾 SAVE
    # =========================
    data["decision"] = action

    data["log"].append(
        f"decision: {action} | analysis: {analysis_type} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
