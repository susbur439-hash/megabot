import random


def decision(data):
    memory = data.get("memory", [])
    evaluation = data.get("evaluation", {})
    goal = data.get("goal", {})
    experience = data.get("experience", [])

    data.setdefault("log", [])

    score = evaluation.get("score", 50)
    progress = goal.get("progress", 0)
    analysis_type = data.get("analysis")
    behavior = data.get("behavior", "balanced")
    trend = data.get("trend", "stable")

    # =========================
    # 🧠 ОПЫТ
    # =========================
    module_scores = {}

    for exp in experience:
        if isinstance(exp, dict):
            m = exp.get("module")
            s = exp.get("score", 0)

            if m:
                module_scores.setdefault(m, []).append(s)

    best_module = None
    best_score = 0

    for m, scores in module_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            if avg > best_score:
                best_score = avg
                best_module = m

    has_strong_module = best_score >= 75
    has_any_module = len(module_scores) > 0

    # =========================
    # 🧠 АНТИ-ЗАЦИКЛИВАНИЕ
    # =========================
    recent = memory[-5:] if len(memory) >= 5 else memory

    too_many_ideas = recent.count("generate_idea") >= 3
    too_many_adds = recent.count("add_module") >= 4
    too_many_runs = recent.count("run_module") >= 3

    stagnation = (
        trend == "stable"
        and score < 70
        and too_many_runs
    )

    # =========================
    # 🎲 ДИНАМИКА ИССЛЕДОВАНИЯ
    # =========================
    if behavior == "aggressive":
        explore_chance = 0.7
    elif behavior == "exploit":
        explore_chance = 0.1
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
            action = "generate_idea"

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
    # 🔥 ЗАЩИТА (важный фикс)
    # =========================
    if action == "do_nothing":
        action = "generate_idea"

    # защита от зацикливания на идеях
    if too_many_ideas and action == "generate_idea":
        action = "add_module"

    # защита от бесконечного добавления
    if too_many_adds and action == "add_module":
        action = "run_module"

    data["decision"] = action

    # =========================
    # 📘 ЛОГ
    # =========================
    data["log"].append(
        f"decision: {action} | analysis: {analysis_type} | behavior: {behavior} | trend: {trend} | score: {score} | best: {best_module}({best_score})"
    )

    return data
