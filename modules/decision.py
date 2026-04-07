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

    # =========================
    # 🧠 СТАТИСТИКА ОПЫТА
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
        avg = sum(scores) / len(scores)
        if avg > best_score:
            best_score = avg
            best_module = m

    has_strong_module = best_score >= 75
    has_any_module = len(module_scores) > 0

    # =========================
    # 🧠 ПОВЕДЕНИЕ (анти-зацикливание)
    # =========================
    recent = memory[-5:]

    too_many_ideas = recent.count("generate_idea") >= 3
    too_many_adds = recent.count("add_module") >= 4
    too_many_runs = recent.count("run_module") >= 3

    # =========================
    # 🎲 ДИНАМИЧЕСКИЙ EXPLORE
    # =========================
    if progress < 30:
        explore_chance = 0.6
    elif progress < 70:
        explore_chance = 0.3
    else:
        explore_chance = 0.1

    # =========================
    # 🔥 ЛОГИКА РЕШЕНИЙ
    # =========================

    # 🚨 RECOVERY (выход из тупика)
    if analysis_type == "recovery":
        if not has_any_module:
            action = "add_module"
        elif has_strong_module:
            action = "run_module"
        else:
            action = "generate_idea"

    # 🧱 BOOTSTRAP
    elif analysis_type == "bootstrap":
        action = "add_module"

    # 🏗 BUILD (создание системы)
    elif analysis_type == "build":
        if too_many_adds:
            action = "run_module"
        else:
            action = "add_module"

    # 🔍 EXPLORE (поиск нового)
    elif analysis_type == "explore":
        if too_many_ideas:
            action = "add_module"
        elif has_strong_module and random.random() > explore_chance:
            action = "run_module"
        else:
            action = random.choice([
                "generate_idea",
                "add_module"
            ])

    # 🎯 EXPLOIT (использование лучшего)
    elif analysis_type == "exploit":
        if has_strong_module:
            if too_many_runs:
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
            action = random.choice([
                "run_module",
                "improve_module"
            ])
        else:
            action = "add_module"

    # ❓ FALLBACK
    else:
        if not has_any_module:
            action = "add_module"
        elif score < 40:
            action = "improve_module"
        else:
            action = "generate_idea"

    # =========================
    # 🔥 ФИНАЛЬНАЯ ЗАЩИТА
    # =========================
    if action == "do_nothing":
        action = "generate_idea"

    data["decision"] = action

    # =========================
    # 📘 ЛОГ
    # =========================
    data["log"].append(
        f"decision: {action} | analysis: {analysis_type} | score: {score} | best: {best_module}({best_score})"
    )

    return data
