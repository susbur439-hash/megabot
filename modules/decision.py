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
    # 🧠 CLEAN EXPERIENCE MAP
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

        # стабильность штраф
        if len(scores) < 3:
            avg *= 0.85

        if avg > best_score:
            best_score = avg
            best_module = m

    has_module = best_module is not None and best_score >= 55

    # =========================
    # 🧠 MODE LOGIC (СТАБИЛЬНАЯ)
    # =========================
    if score < 45:
        action = "create_module"
        module = None

    elif score > 75 and has_module:
        action = "run_module"
        module = best_module

    else:
        action = "run_module" if has_module else "create_module"
        module = best_module if has_module else None

    # =========================
    # 🧨 HARD SAFETY CONTRACT
    # =========================
    if action == "run_module" and not module:
        action = "create_module"
        module = None

    # =========================
    # 💾 OUTPUT CONTRACT (ВАЖНО)
    # =========================
    data["decision"] = action
    data["module"] = module

    data["log"].append(
        f"decision: {action} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
