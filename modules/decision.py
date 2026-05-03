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
    # 🌐 INTERNET BIAS (🔥 НОВОЕ)
    # =========================
    internet_weights = data.get("internet_weights", {})

    decision_bias = internet_weights.get("decision:create_module", 0)
    module_bias = internet_weights.get("module", {})

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
        if not scores:
            continue

        avg = sum(scores) / len(scores)

        # стабильность
        if len(scores) < 3:
            avg *= 0.85

        # 🌐 INTERNET BOOST (если есть знания о модуле)
        avg += module_bias.get(m, 0)

        if avg > best_score:
            best_score = avg
            best_module = m

    has_good_module = best_module is not None and best_score >= 45

    # =========================
    # 🧠 CREATE STREAK
    # =========================
    create_streak = data.get("create_repeats", 0)

    # =========================
    # 🧠 DECISION LOGIC (INTERNET-AWARE)
    # =========================

    action = None
    module = None

    # 🔥 ИНТЕРНЕТ СИЛЬНО ХОЧЕТ CREATE → даём шанс
    if decision_bias > 50 and score > 70:
        action = "create_module"

    # ❌ нет опыта
    elif not has_good_module:
        action = "create_module"

    # 🔁 защита от зацикливания
    elif create_streak >= 2:
        action = "run_module"
        module = best_module

    # 📉 низкий score
    elif score < 60:
        action = "run_module"
        module = best_module

    # 📊 средний
    elif score < 85:
        action = "run_module"
        module = best_module

    # 🚀 высокий
    else:
        action = "create_module"

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
    # 📈 UPDATE STREAK
    # =========================
    if action == "create_module":
        data["create_repeats"] = create_streak + 1
    else:
        data["create_repeats"] = 0

    # =========================
    # 🧾 LOG
    # =========================
    data["log"].append(
        f"decision: {action} | score: {score} | best: {best_module}({round(best_score,1)}) | bias:{decision_bias}"
    )

    return data
