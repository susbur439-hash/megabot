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
    # 🧠 STATE MANAGER (ГЛАВНОЕ)
    # =========================
    data = state_manager(data)
    state = data.get("state", {})

    mode = state.get("mode", "explore")
    phase = state.get("phase", "normal")
    trend = state.get("trend", "stable")

    progress = goal.get("progress", 0)
    target = goal.get("target", 100)

    # =========================
    # 🚨 АНТИ-ДЕГРАДАЦИЯ (через state)
    # =========================
    if phase == "crisis":
        data["log"].append("🚨 control: crisis detected")
        data["mode"] = "explore"
        data["force_explore"] = True

    elif phase == "stagnation":
        data["log"].append("🔁 control: stagnation detected")
        data["mode"] = "improve"
        data["force_explore"] = True

    else:
        data["mode"] = mode
        data["force_explore"] = False

    # =========================
    # 🔋 ЭНЕРГИЯ (приоритет)
    # =========================
    if env.get("energy", 100) < 20:
        data["log"].append("🔋 control: low energy → safe mode")
        data["mode"] = "safe"
        data["force_explore"] = False

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

        data["log"].append(f"🚀 CONTROL LEVEL UP → {goal['level']}")

        env["energy"] = min(100, env.get("energy", 100) + 10)
        env["entropy"] = max(0, env.get("entropy", 0) - 3)

    # =========================
    # 🧠 УМНОЕ ПОВЕДЕНИЕ (через state)
    # =========================
    task = data.get("task", "").lower()

    if "файл" in task and progress > 60:
        data["task"] = "создай модуль и улучши систему"
        data["log"].append("🧠 control: shift → module")

    elif "модуль" in task and progress > 70:
        data["task"] = "создай отчет и проанализируй себя"
        data["log"].append("🧠 control: shift → report")

    # =========================
    # 🛡 АНТИ-СПАМ МОДУЛЕЙ
    # =========================
    if len(data["experience"]) >= 5:
        last = [x.get("module") for x in data["experience"][-5:]]
        if len(set(last)) == 1:
            data["log"].append("🚫 control: module spam detected")
            data["force_explore"] = True

    # =========================
    # 📊 СОСТОЯНИЕ
    # =========================
    data["control_state"] = phase

    data["log"].append(
        f"🧠 control: mode={data.get('mode')} | phase={phase} | trend={trend} | progress={progress}/{target}"
    )

    return data
