from modules.control_bus import inject, emit


def decide(data):
    return decision(data)


def decision(data):

    if not isinstance(data, dict):
        data = {}

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("evaluation", {})
    data.setdefault("create_repeats", 0)

    # =========================
    # 🧠 CONTROL BUS INJECT (ВХОД)
    # =========================
    data = inject(data)

    score = data.get("evaluation", {}).get("score", 50)
    experience = data.get("experience", [])

    # =========================
    # 🌐 INTERNET + SNAPSHOT BIAS
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
    best_score = -1

    for m, scores in module_map.items():
        avg = sum(scores) / len(scores)

        if len(scores) < 2:
            avg *= 0.8

        if avg > best_score:
            best_score = avg
            best_module = m

    has_modules = len(module_map) > 0
    has_good_module = best_module is not None and best_score >= 40

    create_streak = data.get("create_repeats", 0)

    action = None
    module = None

    # =========================
    # 🚨 SAFE DECISION CORE (ЖЁСТКИЙ)
    # =========================

    # 1. если есть хороший модуль → ВСЕГДА run
    if has_good_module:
        action = "run_module"
        module = best_module

    # 2. если есть любые модули → тоже run
    elif has_modules:
        action = "run_module"
        module = best_module

    # 3. только если вообще ничего нет → create (и то ограничено)
    elif create_streak < 1:
        action = "create_module"

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
    # 🧹 CLEANUP SIGNAL
    # =========================
    cleanup_list = []

    for m, scores in module_map.items():
        avg = sum(scores) / len(scores)

        if avg < 20 and len(scores) >= 2:
            cleanup_list.append(m)

    if cleanup_list:
        data["cleanup_modules"] = cleanup_list
        data["log"].append(f"🧹 cleanup candidates: {cleanup_list}")

    # =========================
    # 📡 CONTROL BUS FEEDBACK
    # =========================
    emit({
        "phase": "decision",
        "action": action,
        "module": module,
        "score": score,
        "modules": len(module_map),
        "best_score": best_score
    })

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
        f"decision: {action} | score: {score} | best: {best_module}({round(best_score,1)}) | modules:{len(module_map)} | bias:{decision_bias:.2f}"
    )

    return data
