def decide(data):
    return decision(data)


def decision(data):

    if not isinstance(data, dict):
        data = {}

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("evaluation", {})

    score = data.get("evaluation", {}).get("score", 50)
    experience = data.get("experience", [])

    # =========================
    # 🧠 EXPERIENCE MAP
    # =========================
    module_map = {}

    for e in experience:
        if not isinstance(e, dict):
            continue

        m = e.get("module")
        s = e.get("score")

        if m is None or s is None:
            continue

        if not isinstance(s, (int, float)):
            continue

        module_map.setdefault(m, []).append(s)

    # =========================
    # 🧠 BEST MODULE SEARCH
    # =========================
    best_module = None
    best_score = 0

    for m, scores in module_map.items():
        if not scores:
            continue

        avg = sum(scores) / len(scores)

        # штраф за нестабильность
        if len(scores) < 3:
            avg *= 0.85

        if avg > best_score:
            best_score = avg
            best_module = m

    # =========================
    # 🔥 УМНЫЙ ПОРОГ
    # =========================
    has_good_module = best_module is not None and best_score >= 45

    # =========================
    # 🧠 ЛОГИКА РЕШЕНИЯ (ФИКС ЦИКЛА)
    # =========================

    create_streak = data.get("create_repeats", 0)

    # 1) если нет модулей → создаём
    if not has_good_module:
        action = "create_module"
        module = None

    # 2) если уже много create подряд → заставляем использовать модуль
    elif create_streak >= 2:
        action = "run_module"
        module = best_module

    # 3) нормальный режим
    else:
        if score < 55:
            action = "run_module"
            module = best_module
        elif score < 80:
            action = "run_module"
            module = best_module
        else:
            action = "create_module"
            module = None

    # =========================
    # 🧨 SAFETY LOCK
    # =========================
    if action == "run_module" and not module:
        action = "create_module"
        module = None

    # =========================
    # 📦 OUTPUT
    # =========================
    data["decision"] = action
    data["module"] = module

    data["log"].append(
        f"decision: {action} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
