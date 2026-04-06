import random


def decision(data):
    memory = data.get("memory", [])
    evaluation = data.get("evaluation", {})
    goal = data.get("goal", {})
    experience = data.get("experience", [])

    score = evaluation.get("score", 50)
    progress = goal.get("progress", 0)

    # 🔥 НАХОДИМ ЛУЧШИЙ МОДУЛЬ (С ЗАЩИТОЙ)
    best_module = None
    best_score = 0

    for exp in experience:
        if isinstance(exp, dict):
            exp_score = exp.get("score", 0)
            exp_module = exp.get("module")

            if exp_score > best_score:
                best_score = exp_score
                best_module = exp_module

    # 🧠 ФЛАГ: есть ли реально хороший модуль
    has_strong_module = best_module is not None and best_score >= 70

    # 🔥 АДАПТИВНЫЙ ШАНС ИССЛЕДОВАНИЯ (улучшение)
    if progress < 30:
        explore_chance = 0.5   # много исследуем
    elif progress < 70:
        explore_chance = 0.3   # баланс
    else:
        explore_chance = 0.1   # почти не рискуем

    analysis_type = data.get("analysis")

    if analysis_type == "self_development":
        data["decision"] = "add_module"
        data["result"] = "System wants to add a new module"

    elif analysis_type == "change_strategy":
        improve_count = memory.count("improve_module")
        run_count = memory.count("run_module")

        if score < 30:
            data["decision"] = "create_alternative"
            data["result"] = "System escapes bad path"

        elif has_strong_module:
            if random.random() < explore_chance:
                data["decision"] = "create_alternative"
                data["result"] = "Exploring despite good solution"
            else:
                data["decision"] = "run_module"
                data["result"] = f"Using best module: {best_module} ({best_score})"

        elif len(experience) < 3:
            data["decision"] = "create_alternative"
            data["result"] = "System gathers experience"

        elif improve_count < 2:
            data["decision"] = "improve_module"
            data["result"] = "System improves module"

        elif run_count < 1:
            data["decision"] = "run_module"
            data["result"] = "System runs module"

        else:
            data["decision"] = "create_alternative"
            data["result"] = "Fallback explore"

    elif analysis_type == "explore":
        if has_strong_module:
            if random.random() < explore_chance:
                data["decision"] = "create_alternative"
                data["result"] = "Exploring new path"
            else:
                data["decision"] = "run_module"
                data["result"] = f"Exploit best module: {best_module} ({best_score})"
        else:
            data["decision"] = "create_alternative"
            data["result"] = "Exploring new path"

    # 🔥 НОВОЕ СОСТОЯНИЕ (из analysis)
    elif analysis_type == "exploit":
        if has_strong_module:
            data["decision"] = "run_module"
            data["result"] = f"Focused exploit: {best_module} ({best_score})"
        else:
            data["decision"] = "create_alternative"
            data["result"] = "No strong module, fallback explore"

    else:
        data["decision"] = "do_nothing"
        data["result"] = "No action"

    data["log"].append(
        f"decision made (score: {score}, progress: {progress}, best: {best_module}, best_score: {best_score}, explore_chance: {explore_chance})"
    )

    return data
