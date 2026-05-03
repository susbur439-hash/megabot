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

        # небольшой штраф за нестабильность
        if len(scores) < 3:
            avg *= 0.9

        if avg > best_score:
            best_score = avg
            best_module = m

    has_any_module = best_module is not None

    # =========================
    # 🧠 НОВАЯ ЛОГИКА (БЕЗ ЗАСТРЕВАНИЯ)
    # =========================
    if not has_any_module:
        action = "create_module"
        module = None

    else:
        # 🔥 ключ: сначала пробуем использовать
        if score < 60:
            action = "run_module"
            module = best_module
        elif score < 80:
            action = "run_module"
            module = best_module
        else:
            action = "create_module"
            module = None

    # =========================
    # 🧨 SAFETY
    # =========================
    if action == "run_module" and not module:
        action = "create_module"
        module = None

    # =========================
    # 💾 OUTPUT
    # =========================
    data["decision"] = action
    data["module"] = module

    data["log"].append(
        f"decision: {action} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
