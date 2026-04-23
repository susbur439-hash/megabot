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
    # 🧠 EXPERIENCE ANALYSIS
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

            # штраф за нестабильность
            if len(scores) < 3:
                avg *= 0.85

            if avg > best_score:
                best_score = avg
                best_module = m

    has_strong_module = best_score >= 65
    has_any_module = len(module_scores) > 0

    # =========================
    # 🚨 MEMORY CONTROL
    # =========================
    recent = memory[-7:]

    too_many_creates = recent.count("create_module") >= 3
    too_many_runs = recent.count("run_module") >= 4
    too_many_improves = recent.count("improve_module") >= 3

    # =========================
    # 🧠 STAGNATION DETECTION (УЛУЧШЕНО)
    # =========================
    stagnation = (
        trend == "stable"
        and score < 70
        and (too_many_runs or too_many_improves)
    )

    heavy_create_loop = recent.count("create_module") >= 4

    # =========================
    # 🚨 BOOTSTRAP (СТРОГИЙ КОНТРОЛЬ)
    # =========================
    if not has_any_module:
        if memory.count("create_module") < 2:
            action = "create_module"
        else:
            action = "run_module"

        data["decision"] = action
        data["log"].append(f"decision: {action} | BOOTSTRAP")
        return data

    # =========================
    # 🔥 MAIN LOGIC (УЛУЧШЕННАЯ)
    # =========================

    if analysis_type == "recovery":
        action = "run_module" if has_strong_module else "improve_module"

    elif analysis_type == "bootstrap":
        action = "create_module"

    elif analysis_type == "build":
        if heavy_create_loop:
            action = "run_module"
        else:
            action = "create_module"

    elif analysis_type == "explore":
        if stagnation:
            action = "improve_module"
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
            action = "improve_module" if too_many_improves else "run_module"
        else:
            action = "create_module"

    elif analysis_type == "optimize":
        action = "run_module" if has_strong_module else "improve_module"

    else:
        # безопасный дефолт
        action = "run_module" if score >= 55 else "improve_module"

    # =========================
    # 🛡 HARD SAFETY FIXES
    # =========================

    # стоп бесконечного создания
    if too_many_creates and action == "create_module":
        action = "run_module"

    # стоп бесконечного run
    if too_many_runs and action == "run_module":
        action = "improve_module"

    # стоп мусорных действий
    if action not in ["create_module", "run_module", "improve_module"]:
        action = "run_module"

    # =========================
    # 📈 PROGRESS BIAS (ВАЖНО)
    # =========================

    # если совсем нет прогресса — толкаем к улучшению
    if progress < 20 and action == "run_module":
        action = "improve_module"

    # =========================
    # 💾 SAVE
    # =========================
    data["decision"] = action

    data["log"].append(
        f"decision: {action} | analysis: {analysis_type} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
