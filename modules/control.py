from modules.state_manager import run as state_manager


def control(data):
    data.setdefault("log", [])
    data.setdefault("goal", {"progress": 0, "target": 100, "level": 1})
    data.setdefault("experience", [])
    data.setdefault("env", {})
    data.setdefault("errors", [])

    env = data["env"]
    goal = data["goal"]

    # =========================
    # 🧠 STATE MANAGER (источник состояния)
    # =========================
    data = state_manager(data)
    state = data.get("state", {})

    mode = state.get("mode", "explore")
    phase = state.get("phase", "normal")

    progress = goal.get("progress", 0)
    target = goal.get("target", 100)

    # =========================
    # 🧠 DEFAULT MODE FROM STATE
    # =========================
    final_mode = mode

    # =========================
    # 🚨 CRISIS / STAGNATION OVERRIDE
    # =========================
    if phase == "crisis":
        data["log"].append("🚨 control: crisis detected")
        final_mode = "explore"

    elif phase == "stagnation":
        data["log"].append("🔁 control: stagnation detected")
        final_mode = "explore"

    # =========================
    # 🔋 ENERGY SAFETY OVERRIDE
    # =========================
    if env.get("energy", 100) < 20:
        data["log"].append("🔋 control: low energy → safe mode")
        final_mode = "safe"

    # =========================
    # 🧹 ENTROPY CONTROL
    # =========================
    if env.get("entropy", 0) > 15:
        data["log"].append("🧹 control: entropy cleanup")
        env["entropy"] = max(0, env["entropy"] - 5)

    # =========================
    # 🚀 LEVEL SYSTEM
    # =========================
    if progress >= target:
        goal["level"] += 1
        goal["progress"] = 0
        goal["target"] = int(target * 1.2)

        data["log"].append(f"🚀 LEVEL UP → {goal['level']}")

        env["energy"] = min(100, env.get("energy", 100) + 10)
        env["entropy"] = max(0, env.get("entropy", 0) - 3)

    # =========================
    # 🛡 ANTI-SPAM MODULES
    # =========================
    if len(data["experience"]) >= 5:
        last = [x.get("module") for x in data["experience"][-5:]]
        if len(set(last)) == 1:
            data["log"].append("🚫 control: module spam detected")
            final_mode = "explore"

    # =========================
    # 📌 FINAL OUTPUT CONTRACT (ВАЖНО)
    # =========================
    data["mode"] = final_mode
    data["control_state"] = phase

    data["log"].append(
        f"🧠 control: mode={final_mode} | phase={phase} | progress={progress}/{target}"
    )

    return data
