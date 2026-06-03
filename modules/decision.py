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
    # 🧠 CONTROL BUS INJECT
    # =========================
    data = inject(data)

    control_state = data.get("control_state", {})
    control_flags = data.get("control_flags", {})

    score = data.get("evaluation", {}).get("score", 50)
    experience = data.get("experience", [])

    # =========================
    # 🚨 HARD BLOCKS
    # =========================
    system_block_create = (
        control_flags.get("overcreate", False)
        or control_flags.get("loop_detected", False)
        or control_state.get("mode") == "repair"
    )

    # =========================
    # 🧠 EXPERIENCE MAP
    # =========================
    module_map = {}

    for e in experience:
        if not isinstance(e, dict):
            continue

        m = e.get("module")
        s = e.get("score")

        if not m or not isinstance(s, (int, float)):
            continue

        module_map.setdefault(m, []).append(s)

    # =========================
    # 🧠 BEST MODULE
    # =========================
    best_module = None
    best_score = -1

    for m, scores in module_map.items():
        avg = sum(scores) / len(scores)

        if len(scores) < 2:
            avg *= 0.85

        if avg > best_score:
            best_score = avg
            best_module = m

    has_modules = len(module_map) > 0
    has_good_module = best_module is not None and best_score >= 40

    create_streak = data.get("create_repeats", 0)

    action = None
    module = None

    # =========================
    # 🚨 CORE LOGIC
    # =========================

    if has_good_module:
        action = "run_module"
        module = best_module

    elif has_modules:
        action = "run_module"
        module = best_module

    elif system_block_create:
        action = "run_module"
        module = best_module

    elif create_streak == 0:
        action = "create_module"

    else:
        action = "run_module"
        module = best_module

    # =========================
    # 🧨 SAFETY FIX
    # =========================
    if action == "run_module" and not module:
        action = "run_module"
        module = "director"

    # =========================
    # 🧹 CLEANUP DETECTION
    # =========================
    cleanup_list = []

    for m, scores in module_map.items():
        avg = sum(scores) / len(scores)

        if len(scores) >= 2 and avg < 20:
            cleanup_list.append(m)

    if cleanup_list:
        data["cleanup_modules"] = cleanup_list

        emit({
            "phase": "cleanup",
            "action": "delete_modules",
            "modules": cleanup_list
        })

    # =========================
    # 📡 CONTROL EVENT
    # =========================
    emit({
        "phase": "decision",
        "action": action,
        "module": module,
        "score": score,
        "modules": len(module_map),
        "blocked": system_block_create
    })

    # =========================
    # 📦 OUTPUT
    # =========================
    data["decision"] = action
    data["module"] = module

    # =========================
    # 📈 STREAK
    # =========================
    if action == "create_module":
        data["create_repeats"] = create_streak + 1
    else:
        data["create_repeats"] = 0

    # =========================
    # 🧾 LOG
    # =========================
    best_score_safe = round(best_score, 1) if best_score != -1 else 0

    data["log"].append(
        f"decision={action} score={score} best={best_module}({best_score_safe}) modules={len(module_map)} blocked={system_block_create}"
    )

    return data