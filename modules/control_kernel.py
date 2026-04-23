import copy
from collections import Counter

def control_kernel(data):
    """
    🧠 CONTROL KERNEL vMAX
    - единый арбитр системы
    - анализирует конфликт состояния
    - может вмешиваться в decision
    - имеет безопасные режимы
    """

    data = copy.deepcopy(data)
    data.setdefault("log", [])

    # =========================
    # 📦 INPUTS
    # =========================
    analysis = data.get("analysis")
    state = data.get("state", {}) or {}
    control = data.get("control_state") or {}
    memory = data.get("memory", []) or []
    evaluation = data.get("evaluation", {}) or {}

    score = evaluation.get("score", 50)
    trend = data.get("local_trend", "stable")
    progress = data.get("goal", {}).get("progress", 0)

    # =========================
    # 🧠 NORMALIZATION
    # =========================
    signals = []

    if analysis:
        signals.append(analysis)

    if isinstance(state, dict):
        signals.append(state.get("mode"))
        signals.append(state.get("phase"))

    if isinstance(control, dict):
        signals.append(control.get("mode"))
        signals.append(control.get("phase"))
    else:
        signals.append(control)

    signals = [s for s in signals if s]

    signal_map = Counter(signals)
    dominant = signal_map.most_common(1)[0][0] if signal_map else "explore"

    # =========================
    # 🚨 SYSTEM STATE CHECK
    # =========================
    conflict = len(signal_map) >= 3

    crisis = (
        "crisis" in signals
        or score < 45
        or trend == "down"
    )

    stagnation = (
        trend == "stable"
        and score < 70
        and memory[-6:].count("run_module") >= 3
    )

    overload_create = memory[-6:].count("create_module") >= 4
    overload_run = memory[-6:].count("run_module") >= 4

    # =========================
    # 🧠 STRATEGY HISTORY
    # =========================
    strategy_history = data.get("strategy_history", [])[-10:]
    current_strategy = data.get("strategy", "explore")

    switches = sum(
        1 for i in range(1, len(strategy_history))
        if strategy_history[i] != strategy_history[i - 1]
    )

    unstable_strategy = switches >= 4

    # =========================
    # 🧭 GLOBAL MODE
    # =========================
    if crisis:
        global_mode = "repair"

    elif stagnation:
        global_mode = "stabilize"

    elif conflict:
        global_mode = "harmonize"

    else:
        global_mode = dominant

    # =========================
    # 🔥 DECISION ENGINE
    # =========================
    action = "run_module"

    if global_mode == "repair":
        action = "improve_module"

    elif global_mode == "stabilize":
        action = "run_module"

    elif global_mode == "harmonize":
        action = "run_module"

    elif global_mode == "explore":
        action = "create_module"

    elif global_mode == "build":
        action = "create_module"

    elif global_mode == "exploit":
        action = "run_module"

    elif global_mode == "improve":
        action = "improve_module"

    # =========================
    # 🛡 SAFETY LAYERS
    # =========================

    if overload_create:
        action = "run_module"

    if overload_run:
        action = "improve_module"

    if unstable_strategy:
        action = "stabilize"

    # =========================
    # ⚖️ SOFT OPTIMIZATION LAYER
    # =========================

    if progress < 20 and action == "run_module":
        action = "improve_module"

    if score < 40:
        action = "improve_module"

    if score > 80 and action == "improve_module":
        action = "run_module"

    # =========================
    # 🧠 OVERRIDE SYSTEM
    # =========================
    override = False

    if crisis and stagnation:
        action = "improve_module"
        override = True

    elif conflict and score < 55:
        action = "run_module"
        override = True

    # =========================
    # 🧾 FINAL STATE WRITEBACK
    # =========================
    data["decision"] = action
    data["strategy"] = global_mode
    data["control_mode"] = global_mode
    data["kernel_override"] = override

    data.setdefault("strategy_history", []).append(global_mode)

    # =========================
    # 📊 LOGGING
    # =========================
    data["log"].append(
        f"🧠 KERNEL vMAX | mode={global_mode} | action={action} | "
        f"score={score} | conflict={conflict} | crisis={crisis} | override={override}"
    )

    return data
