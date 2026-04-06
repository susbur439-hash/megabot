import random


def decision(data):
    memory = data.get("memory", [])
    evaluation = data.get("evaluation", {})
    goal = data.get("goal", {})
    experience = data.get("experience", [])

    data.setdefault("log", [])

    score = evaluation.get("score", 50)
    progress = goal.get("progress", 0)

    # 🧠 лучший модуль
    best_module = None
    best_score = 0

    for exp in experience:
        if isinstance(exp, dict):
            if exp.get("score", 0) > best_score:
                best_score = exp["score"]
                best_module = exp.get("module")

    has_strong_module = best_module is not None and best_score >= 70

    # 🎲 explore шанс
    if progress < 30:
        explore_chance = 0.5
    elif progress < 70:
        explore_chance = 0.3
    else:
        explore_chance = 0.1

    analysis_type = data.get("analysis")

    # =====================================================
    # 🔥 RECOVERY
    # =====================================================
    if analysis_type == "recovery":
        if len(experience) == 0:
            data["decision"] = "add_module"
        elif has_strong_module:
            data["decision"] = "run_module"
        else:
            data["decision"] = "create_alternative"

    # =====================================================
    # 🧱 BOOTSTRAP
    # =====================================================
    elif analysis_type == "bootstrap":
        data["decision"] = "add_module"

    # =====================================================
    # 🏗 BUILD
    # =====================================================
    elif analysis_type == "build":
        data["decision"] = "add_module"

    # =====================================================
    # 🔍 EXPLORE
    # =====================================================
    elif analysis_type == "explore":
        if has_strong_module and random.random() > explore_chance:
            data["decision"] = "run_module"
        else:
            data["decision"] = "generate_idea"

    # =====================================================
    # 🎯 EXPLOIT
    # =====================================================
    elif analysis_type == "exploit":
        if has_strong_module:
            data["decision"] = "run_module"
        else:
            data["decision"] = "generate_idea"

    # =====================================================
    # 🛠 IMPROVE
    # =====================================================
    elif analysis_type == "improve":
        data["decision"] = "improve_module"

    # =====================================================
    # ⚡ OPTIMIZE
    # =====================================================
    elif analysis_type == "optimize":
        data["decision"] = "improve_module"

    # =====================================================
    # ❌ НИКОГДА НЕ do_nothing
    # =====================================================
    else:
        data["decision"] = "generate_idea"

    # 🔥 ЗАЩИТА
    if data["decision"] == "do_nothing":
        data["decision"] = "generate_idea"

    data["log"].append(
        f"decision: {data['decision']} | analysis: {analysis_type} | score: {score}"
    )

    return data
