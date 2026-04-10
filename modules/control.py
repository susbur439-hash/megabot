# control.py

def control(data):
    data.setdefault("log", [])
    data.setdefault("goal", {"progress": 0, "target": 100, "level": 1})
    data.setdefault("experience", [])
    data.setdefault("env", {})
    data.setdefault("errors", [])

    env = data["env"]
    goal = data["goal"]

    progress = goal.get("progress", 0)
    target = goal.get("target", 100)

    # =========================
    # 📊 АНАЛИЗ СОСТОЯНИЯ
    # =========================
    stagnation = False
    if len(data["experience"]) >= 3:
        last_deltas = [x.get("delta", 0) for x in data["experience"][-3:]]
        if sum(last_deltas) <= 5:
            stagnation = True

    high_entropy = env.get("entropy", 0) > 12
    low_energy = env.get("energy", 100) < 20

    # =========================
    # 🚨 АНТИ-ДЕГРАДАЦИЯ
    # =========================
    if stagnation:
        data["log"].append("🔁 control: stagnation detected")
        data["mode"] = "explore"
        data["force_explore"] = True

    if high_entropy:
        data["log"].append("🧹 control: entropy high → cleanup")
        env["entropy"] = max(0, env["entropy"] - 5)
        data["mode"] = "explore"
        data["force_explore"] = True

    if low_energy:
        data["log"].append("🔋 control: low energy → safe mode")
        data["mode"] = "safe"
        data["force_explore"] = False

    # =========================
    # 🎯 УПРАВЛЕНИЕ СТРАТЕГИЕЙ
    # =========================
    if not stagnation and not high_entropy:
        data["mode"] = "exploit"
        data["force_explore"] = False

    # =========================
    # 🚀 LEVEL SYSTEM
    # =========================
    if progress >= target:
        goal["level"] += 1
        goal["progress"] = 0
        goal["target"] = int(target * 1.2)

        data["log"].append(f"🚀 CONTROL LEVEL UP → {goal['level']}")

        # бонус
        env["energy"] = min(100, env.get("energy", 100) + 10)
        env["entropy"] = max(0, env.get("entropy", 0) - 3)

    # =========================
    # 🧠 УМНОЕ ПЕРЕКЛЮЧЕНИЕ ЗАДАЧ
    # =========================
    task = data.get("task", "").lower()

    if "создай файл" in task and progress > 60:
        data["task"] = "создай модуль и улучши систему"
        data["log"].append("🧠 control: смена задачи → модуль")

    if "модуль" in task and progress > 70:
        data["task"] = "создай отчет и проанализируй себя"
        data["log"].append("🧠 control: смена задачи → отчет")

    # =========================
    # 🛡 ЗАЩИТА ОТ СПАМА
    # =========================
    if len(data["experience"]) >= 5:
        last_modules = [x.get("module") for x in data["experience"][-5:]]
        if len(set(last_modules)) == 1:
            data["log"].append("🚫 control: module spam detected")
            data["force_explore"] = True

    # =========================
    # 📈 СОСТОЯНИЕ СИСТЕМЫ
    # =========================
    if stagnation:
        state = "stagnation"
    elif high_entropy:
        state = "chaos"
    elif progress > target * 0.7:
        state = "growth"
    else:
        state = "normal"

    data["control_state"] = state

    data["log"].append(
        f"🧠 control: mode={data.get('mode')} | state={state} | progress={progress}/{target}"
    )

    return data
