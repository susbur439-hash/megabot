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
    trend = data.get("local_trend", "stable")  # 🔥 FIX

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

            # 🔥 анти-доминирование
            if len(scores) < 2:
                avg *= 0.9

            if avg > best_score:
                best_score = avg
                best_module = m

    has_strong_module = best_score >= 75
    has_any_module = len(module_scores) > 0

    # =========================
    # 🧠 АНТИ-ЗАЦИКЛИВАНИЕ
    # =========================
    recent = memory[-5:]

    too_many_ideas = recent.count("generate_idea") >= 3
    too_many_adds = recent.count("add_module") >= 4
    too_many_runs = recent.count("run_module") >= 3
    too_many_improves = recent.count("improve_module") >= 3

    stagnation = (
        trend == "stable"
        and score < 75
        and (too_many_runs or too_many_improves)
    )

    # =========================
    # 🎲 ДИНАМИКА
    # =========================
    if behavior == "aggressive":
        explore_chance = 0.75
    elif behavior == "exploit":
        explore_chance = 0.1
    elif behavior == "explore":
        explore_chance = 0.9
    else:
        explore_chance = 0.3

    # =========================
    # 🔥 ЛОГИКА
    # =========================

    # 🚨 RECOVERY
    if analysis_type == "recovery":
        if not has_any_module:
            action = "add_module"
        elif has_strong_module:
            action = "run_module"
        else:
            action = "improve_module"

    # 🧱 BOOTSTRAP
    elif analysis_type == "bootstrap":
        action = "add_module"

    # 🏗 BUILD
    elif analysis_type == "build":
        if too_many_adds:
            action = "run_module"
        else:
            action = "add_module"

    # 🔍 EXPLORE
    elif analysis_type == "explore":

        if stagnation:
            action = "add_module"

        elif too_many_ideas:
            action = "add_module"

        elif has_strong_module and random.random() > explore_chance:
            action = "run_module"

        else:
            action = random.choice([
                "generate_idea",
                "add_module"
            ])  # 🔥 усилено

    # 🎯 EXPLOIT
    elif analysis_type == "exploit":

        if has_strong_module:

            if too_many_runs or stagnation:
                action = "improve_module"
            else:
                action = "run_module"

        else:
            action = "add_module"

    # 🛠 IMPROVE
    elif analysis_type == "improve":

        if has_strong_module:
            if too_many_improves:
                action = "run_module"
            else:
                action = "improve_module"
        else:
            action = "add_module"

    # ⚡ OPTIMIZE
    elif analysis_type == "optimize":

        if has_strong_module:

            if behavior == "exploit":
                action = "run_module"
            else:
                action = "improve_module"

        else:
            action = "add_module"

    # ❓ FALLBACK
    else:
        if not has_any_module:
            action = "add_module"
        elif score < 50:
            action = "improve_module"
        else:
            action = "generate_idea"

    # =========================
    # 🛡 ЗАЩИТА
    # =========================
    if action == "do_nothing":
        action = "generate_idea"

    if too_many_ideas and action == "generate_idea":
        action = "add_module"

    if too_many_adds and action == "add_module":
        action = "run_module"

    if too_many_runs and action == "run_module":
        action = "improve_module"

    # =========================
    # 💾 SAVE
    # =========================
    data["decision"] = action

    # =========================
    # 📘 LOG
    # =========================
    data["log"].append(
        f"decision: {action} | analysis: {analysis_type} | behavior: {behavior} | trend: {trend} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
