def set_goal(data):

    if "goal" not in data or not isinstance(data["goal"], dict):
        data["goal"] = {}

    goal = data["goal"]

    goal.setdefault("name", data.get("task_type", "adaptive_goal"))
    goal.setdefault("progress", 0)
    goal.setdefault("level", 1)
    goal.setdefault("target", 100)
    goal.setdefault("history", [])

    data.setdefault("prev_progress", goal["progress"])

    return data


def update_goal(data):

    goal = data.get("goal", {})
    progress = goal.get("progress", 0)
    prev_progress = data.get("prev_progress", progress)

    level = goal.get("level", 1)
    target = goal.get("target", 100)

    data.setdefault("log", [])

    # =========================
    # 🔥 ЧИСТЫЙ REAL DELTA
    # =========================
    real_delta = progress - prev_progress
    data["last_delta"] = real_delta

    # =========================
    # ❗ НЕ ТРОГАЕМ progress
    # =========================
    # progress уже изменён execution
    # тут только анализ

    # =========================
    # 📊 HISTORY + TREND
    # =========================
    history = goal.get("history", [])
    history.append(real_delta)
    history = history[-10:]

    avg = sum(history) / len(history) if history else 0

    if avg > 5:
        trend = "up"
    elif avg < 0:
        trend = "down"
    else:
        trend = "stable"

    goal["history"] = history
    data["trend"] = trend

    # =========================
    # 🔥 LEVEL SYSTEM (ФИКС)
    # =========================
    leveled_up = False

    if progress >= target:
        level += 1
        progress = progress - target
        target = int(target * 1.2)

        goal["target"] = target
        data["difficulty"] = level
        leveled_up = True

        data["log"].append(f"🚀 LEVEL UP → {level}")

    elif progress < 0:
        progress = 0

    # =========================
    # 🔥 КОРРЕКЦИЯ DELTA ПРИ LEVEL UP
    # =========================
    if leveled_up:
        data["last_delta"] = max(real_delta, 1)

    # =========================
    # 🧠 STATE
    # =========================
    if trend == "down":
        state = "crisis"
    elif trend == "up":
        state = "growth"
    elif progress > target * 0.8:
        state = "finishing"
    else:
        state = "normal"

    goal["state"] = state

    # =========================
    # 📦 SAVE
    # =========================
    goal["progress"] = min(progress, target)
    goal["level"] = level

    data["goal"] = goal
    data["prev_progress"] = goal["progress"]

    # =========================
    # 📘 LOG
    # =========================
    data["log"].append(
        f"{goal['name']}: {goal['progress']}/{target} | level: {level} | trend: {trend} | state: {state} | delta: {data['last_delta']}"
    )

    return data
