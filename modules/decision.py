def decide(data):
    return decision(data)


def decision(data):

    if not isinstance(data, dict):
        data = {}

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("evaluation", {})

    score = data["evaluation"].get("score", 50)
    experience = data["experience"]

    # =========================
    # 🧠 поиск лучшего модуля
    # =========================
    best_module = None
    best_score = 0

    module_map = {}

    for e in experience:
        if not isinstance(e, dict):
            continue

        m = e.get("module")
        s = e.get("score", 0)

        if m:
            module_map.setdefault(m, []).append(s)

    for m, scores in module_map.items():
        avg = sum(scores) / len(scores)
        if avg > best_score:
            best_score = avg
            best_module = m

    has_module = best_module is not None and best_score >= 50

    # =========================
    # 🧠 ЖЁСТКАЯ ЛОГИКА (без пустоты)
    # =========================
    if score < 45:
        action = "create_module"
        module = None

    elif score > 75 and has_module:
        action = "run_module"
        module = best_module

    else:
        # 🔥 ВАЖНО: НЕТ СТЕЙТА "НИЧЕГО"
        if has_module:
            action = "run_module"
            module = best_module
        else:
            action = "create_module"
            module = None

    # =========================
    # 🧨 АНТИ-ЗАВИСАНИЕ
    # =========================
    if action == "run_module" and not module:
        action = "create_module"
        module = None

    data["decision"] = action
    data["module"] = module

    data["log"].append(
        f"decision: {action} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
