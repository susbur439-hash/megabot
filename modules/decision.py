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
    # 🧠 EXPERIENCE ANALYSIS (УЛУЧШЕНО)
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
        if not scores:
            continue

        avg = sum(scores) / len(scores)

        # штраф за нестабильность
        variance_penalty = abs(max(scores) - min(scores)) if len(scores) > 1 else 0
        avg -= variance_penalty * 0.05

        # штраф за малый опыт
        if len(scores) < 3:
            avg *= 0.8

        if avg > best_score:
            best_score = avg
            best_module = m

    has_strong_module = best_score >= 65
    has_any_module = len(module_scores) > 0

    # =========================
    # 🧠 PATTERN DETECTION (НОВОЕ)
    # =========================
    recent = memory[-10:]

    def count(x):
        return recent.count(x)

    too_many_creates = count("create_module") >= 3
    too_many_runs = count("run_module") >= 4
    too_many_improves = count("improve_module") >= 3

    heavy_create_loop = count("create_module") >= 5
    full_loop_stuck = too_many_creates and too_many_runs

    # =========================
    # 📉 STAGNATION DETECTION (УЛУЧШЕНО)
    # =========================
    stagnation = (
        trend == "stable"
        and score < 70
        and (too_many_runs or too_many_improves)
    )

    no_real_progress = progress < 25 and score < 60

    # =========================
    # 🚨 BOOTSTRAP CONTROL
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
    # 🧠 MODE SWITCHING (НОВОЕ)
    # =========================
    if stagnation and heavy_create_loop:
        mode = "stabilize"
    elif score >= 70 and has_strong_module:
        mode = "exploit"
    elif score < 50:
        mode = "explore"
    else:
        mode = analysis_type

    # =========================
    # 🔥 MAIN LOGIC
    # =========================

    if mode == "recovery":
        action = "run_module" if has_strong_module else "improve_module"

    elif mode == "bootstrap":
        action = "create_module"

    elif mode == "build":
        action = "run_module" if heavy_create_loop else "create_module"

    elif mode == "explore":
        if stagnation or no_real_progress:
            action = "improve_module"
        elif has_strong_module:
            action = "run_module"
        else:
            action = "create_module"

    elif mode == "exploit":
        if has_strong_module:
            if stagnation or too_many_runs:
                action = "improve_module"
            else:
                action = "run_module"
        else:
            action = "create_module"

    elif mode == "improve":
        if has_strong_module:
            action = "improve_module" if too_many_improves else "run_module"
        else:
            action = "create_module"

    elif mode == "optimize":
        action = "run_module" if has_strong_module else "improve_module"

    elif mode == "stabilize":
        # 🔥 НОВЫЙ РЕЖИМ — ВАЖНЕЙШИЙ
        if has_strong_module:
            action = "improve_module"
        else:
            action = "run_module"

    else:
        action = "run_module" if score >= 55 else "improve_module"

    # =========================
    # 🛡 HARD SAFETY FIXES
    # =========================

    if too_many_creates and action == "create_module":
        action = "run_module"

    if too_many_runs and action == "run_module":
        action = "improve_module"

    if full_loop_stuck:
        action = "stabilize"

    if action not in ["create_module", "run_module", "improve_module"]:
        action = "run_module"

    # =========================
    # 📈 PROGRESS FORCE (НОВОЕ)
    # =========================

    if progress < 20 and action == "run_module":
        action = "improve_module"

    # если система “живая но не растёт”
    if no_real_progress and action == "run_module":
        action = "improve_module"

    # =========================
    # 💾 SAVE
    # =========================
    data["decision"] = action

    data["log"].append(
        f"decision: {action} | mode: {mode} | analysis: {analysis_type} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
