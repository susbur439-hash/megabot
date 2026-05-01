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
    # 🧠 STATE MANAGER
    # =========================
    data = state_manager(data)
    state = data.get("state", {})

    mode = state.get("mode", "explore")
    phase = state.get("phase", "normal")

    progress = goal.get("progress", 0)
    target = goal.get("target", 100)

    # =========================
    # 🚨 CRISIS FLAGS
    # =========================
    if phase == "crisis":
        data["log"].append("🚨 control: crisis detected")
        data["force_explore"] = True

    elif phase == "stagnation":
        data["log"].append("🔁 control: stagnation detected")
        data["force_explore"] = True

    # =========================
    # 🔋 ENERGY LIMIT
    # =========================
    if env.get("energy", 100) < 20:
        data["log"].append("🔋 control: low energy → safe mode")
        data["force_safe"] = True

    # =========================
    # 🧹 ENTROPY CLEANUP
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
    # 🛡 ANTI-SPAM
    # =========================
    if len(data["experience"]) >= 5:
        last = [x.get("module") for x in data["experience"][-5:]]
        if len(set(last)) == 1:
            data["log"].append("🚫 control: module spam detected")
            data["force_explore"] = True

    # =========================
    # 📊 STATE OUTPUT
    # =========================
    data["control_state"] = phase

    data["log"].append(
        f"🧠 control: mode={mode} | phase={phase} | progress={progress}/{target}"
    )

    return data
