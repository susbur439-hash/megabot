import random


def decision(data):
    memory = data.get("memory", [])
    evaluation = data.get("evaluation", {})
    goal = data.get("goal", {})
    experience = data.get("experience", [])

    score = evaluation.get("score", 50)
    progress = goal.get("progress", 0)

    # =========================
    # 🧠 ЛУЧШИЙ МОДУЛЬ
    # =========================
    best_module = None
    best_score = 0

    for exp in experience:
        if isinstance(exp, dict):
            exp_score = exp.get("score", 0)
            exp_module = exp.get("module")

            if exp_score > best_score:
                best_score = exp_score
                best_module = exp_module

    has_strong_module = best_module is not None and best_score >= 70

    # =========================
    # 🔄 EXPLORE ШАНС
    # =========================
    if progress < 30:
        explore_chance = 0.5
    elif progress < 70:
        explore_chance = 0.3
    else:
        explore_chance = 0.1

    analysis_type = data.get("analysis")

    # =========================================================
    # 🔥🔥🔥 АНТИ-ЗАСТРЕВАНИЕ (САМЫЙ ВАЖНЫЙ БЛОК)
    # =========================================================
    if analysis_type == "recovery":

        # нет опыта → создаем базу
        if len(experience) == 0:
            data["decision"] = "add_module"
            data["result"] = "Recovery: creating first module"

        # есть сильный модуль → форсим его
        elif has_strong_module:
            data["decision"] = "run_module"
            data["result"] = f"Recovery: forcing best module {best_module} ({best_score})"

        # иначе → новый путь
        else:
            data["decision"] = "create_alternative"
            data["result"] = "Recovery: new strategy"

        data["log"].append(
            f"decision (recovery) | best: {best_module} | score: {best_score}"
        )
        return data

    # =========================
    # 🚀 САМОРАЗВИТИЕ
    # =========================
    if analysis_type == "self_development":
        data["decision"] = "add_module"
        data["result"] = "System builds new module"

    # =========================
    # 🔄 СМЕНА СТРАТЕГИИ
    # =========================
    elif analysis_type == "change_strategy":

        improve_count = memory.count("improve_module")
        run_count = memory.count("run_module")

        if score < 30:
            data["decision"] = "create_alternative"
            data["result"] = "Escaping bad path"

        elif has_strong_module:
            if random.random() < explore_chance:
                data["decision"] = "generate_idea"
                data["result"] = "Exploring new idea"
            else:
                data["decision"] = "run_module"
                data["result"] = f"Using best module: {best_module} ({best_score})"

        elif len(experience) < 3:
            data["decision"] = "generate_idea"
            data["result"] = "Gathering ideas"

        elif improve_count < 2:
            data["decision"] = "improve_module"
            data["result"] = "Improving module"

        elif run_count < 1:
            data["decision"] = "run_module"
            data["result"] = "Trying module"

        else:
            data["decision"] = "generate_idea"
            data["result"] = "Fallback idea"

    # =========================
    # 🔍 ИССЛЕДОВАНИЕ
    # =========================
    elif analysis_type == "explore":

        if has_strong_module:
            if random.random() < explore_chance:
                data["decision"] = "generate_idea"
                data["result"] = "Generating idea"
            else:
                data["decision"] = "run_module"
                data["result"] = f"Exploit: {best_module} ({best_score})"
        else:
            data["decision"] = "generate_idea"
            data["result"] = "No strong module → idea"

    # =========================
    # 🎯 ЭКСПЛУАТАЦИЯ
    # =========================
    elif analysis_type == "exploit":

        if has_strong_module:
            data["decision"] = "run_module"
            data["result"] = f"Focused run: {best_module} ({best_score})"
        else:
            data["decision"] = "generate_idea"
            data["result"] = "No best module → idea"

    # =========================
    # ❌ НЕИЗВЕСТНО
    # =========================
    else:
        # 🔥 fallback защита (чтобы НИКОГДА не было do_nothing цикла)
        data["decision"] = "generate_idea"
        data["result"] = "Fallback: generating idea"

    # =========================
    # 📊 ЛОГ
    # =========================
    data["log"].append(
        f"decision made (score: {score}, progress: {progress}, best: {best_module}, best_score: {best_score}, explore: {explore_chance})"
    )

    return data
