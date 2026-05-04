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

        # штраф за малый опыт
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
    # 🚨 SAFE DECISION CORE (УЛУЧШЕН)
    # =========================

    # 1. если есть хороший модуль → всегда используем
    if has_good_module:
        action = "run_module"
        module = best_module

    # 2. если есть модули (даже слабые) → используем лучший
    elif has_modules:
        action = "run_module"
        module = best_module

    # 3. если нет модулей → можно создать (но ограниченно)
    elif create_streak < 2:
        action = "create_module"

    # 4. защита от зацикливания
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
    # 🧹 CLEANUP (НОВОЕ)
    # =========================
    cleanup_list = []

    for m, scores in module_map.items():
        avg = sum(scores) / len(scores)

        # слабые модули → удалить
        if avg < 20 and len(scores) >= 2:
            cleanup_list.append(m)

    if
