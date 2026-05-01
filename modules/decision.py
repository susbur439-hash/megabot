def decide(data):
    return decision(data)


def decision(data):

    if not isinstance(data, dict):
        data = {}

    evaluation = data.get("evaluation") or {}
    experience = data.get("experience") or []

    data.setdefault("log", [])

    score = evaluation.get("score", 50)

    # =========================
    # 🧠 EXPERIENCE ANALYSIS
    # =========================
    module_scores = {}

    for exp in experience:
        if not isinstance(exp, dict):
            continue

        m = exp.get("module")
        s = exp.get("score", 0)

        if m and isinstance(s, (int, float)):
            module_scores.setdefault(m, []).append(s)

    best_module = None
    best_score = 0

    for m, scores in module_scores.items():
        avg = sum(scores) / len(scores)

        if len(scores) < 3:
            avg *= 0.8

        if avg > best_score:
            best_score = avg
            best_module = m

    has_strong_module = best_score >= 65

    # =========================
    # 🧠 MODE
    # =========================
    if score < 45:
        mode = "explore"
    elif score > 75 and has_strong_module:
        mode = "exploit"
    else:
        mode = "balanced"

    # =========================
    # 🔥 DECISION
    # =========================
    if mode == "explore":
        action = "create_module"
        selected_module = None

    elif mode == "exploit":
        action = "run_module"
        selected_module = best_module

    else:
        # ⚠️ ВАЖНО: НЕ ПАДАЕМ В CREATE
        action = "run_module"
        selected_module = best_module

    # =========================
    # 🧠 SAFE CLEAN FALLBACK (ИСПРАВЛЕНО)
    # =========================
    if action == "run_module" and not selected_module:
        # вместо create_module → уходим в explore
        action = "explore"
        selected_module = None

    # =========================
    # 💾 OUTPUT
    # =========================
    data["decision"] = action
    data["module"] = selected_module

    data["log"].append(
        f"decision: {action} | mode: {mode} | score: {score} | best: {best_module}({round(best_score,1)})"
    )

    return data
