def decide(data):
    return decision(data)


def decision(data):

    if not isinstance(data, dict):
        data = {}

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("evaluation", {})
    data.setdefault("create_repeats", 0)

    score = data.get("evaluation", {}).get("score", 50)
    experience = data.get("experience", [])

    # =========================
    # 🌐 INTERNET + SNAPSHOT BIAS (FIXED)
    # =========================
    internet_weights = data.get("internet_weights", {})
    snapshot_bias = data.get("snapshot_bias", {})

    decision_bias = (
        internet_weights.get("decision:create_module", 0)
        + snapshot_bias.get("create", 0)
    )

    run_bias = snapshot_bias.get("run", 0)

    # =========================
    # 🧠 EXPERIENCE MAP
    # =========================
    module_map = {}

    for e in experience:
        if not isinstance(e, dict):
            continue

        m = e.get("module")
        s = e.get("score")

        if not m or s is None:
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
        avg = sum(scores) / len(scores)

        if len(scores) < 3:
            avg *= 0.85

        if avg > best_score:
            best_score = avg
            best_module = m

    has_good_module = best_module is not None and best_score >= 45

    # =========================
    # 🧠 CREATE STREAK
    # =========================
    create_streak = data.get("create_repeats", 0)

    action = None
    module = None

    # =========================
    # 🚨 FIX: SAFE FIRST RULE
    # =========================

    # 1. если есть хороший модуль → всегда run
    if has_good_module and score < 90:
        action = "run_module"
        module = best_module

    # 2. анти-спам create (ВАЖНО)
    elif create_streak >= 2:
        action = "run_module"
        module = best_module

    # 3. низкий score → run, а не create
    elif score < 60:
        action = "run_module"
        module = best_module

    # 4. только при хорошем состоянии создаём
    elif score >= 85 and decision_bias > 0:
        action = "create_module"

    # 5. fallback
    else:
        action = "run_module"
        module = best_module

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

    # =========================
    # 📈 STREAK UPDATE
    # =========================
    if action == "create_module":
        data["create_repeats"] = create_streak + 1
    else:
        data["create_repeats"] = 0

    # =========================
    # 🧾 LOG
    # =========================
    data["log"].append(
        f"decision: {action} | score: {score} | best: {best_module}({round(best_score,1)}) | bias:{decision_bias:.2f}"
    )

    return data
