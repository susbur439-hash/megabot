def set_goal(data):

    if "goal" not in data or not isinstance(data["goal"], dict):
        data["goal"] = {}

    goal = data["goal"]

    goal.setdefault("name", data.get("task_type", "adaptive_goal"))
    goal.setdefault("progress", 0)
    goal.setdefault("level", 1)
    goal.setdefault("target", 100)
    goal.setdefault("history", [])

    # 🔥 ВАЖНО: фиксируем состояние ДО execution
    data["prev_progress"] = goal["progress"]

    return data


def update_goal(data):

    goal = data.get("goal", {})
    progress = goal.get("progress", 0)
    prev_progress = data.get("prev_progress", progress)

    level = goal.get("level", 1)
    target = goal.get("target", 100)

    data.setdefault("log", [])

    # =========================
    # 🔥 REAL DELTA (чистый)
    # =========================
    real_delta = progress - prev_progress

    # защита от мусора
    if abs(real_delta) > 1000:
        real_delta = 0

    data["last_delta"] = real_delta

    # =========================
    # 📊 HISTORY (по SCORE, а не delta)
    # =========================
    score = data.get("evaluation", {}).get("score", 50)

    history = goal.get("history", [])
    history.append(score)
    history = history[-10:]

    avg = sum(history) / len(history) if history else 50

    if avg > 75:
        trend = "up"
    elif avg < 40:
        trend = "down"
    else:
        trend = "stable"

    goal["history"] = history
    data["trend"] = trend

    # =========================
    # 🚀 LEVEL SYSTEM (СТАБИЛЬНЫЙ)
    # =========================
    leveled_up = False

    if progress >= target:
        level += 1

        overflow = progress - target
        progress = overflow

        target = int(target * 1.2)

        goal["target"] = target
        data["difficulty"] = level

        leveled_up = True
        data["log"].append(f"🚀 LEVEL UP → {level}")

    elif progress < 0:
        progress = 0

    # =========================
    # 🔥 DELTA FIX ПРИ LEVEL UP
    # =========================
    if leveled_up:
        real_delta = max(real_delta, 1)
        data["last_delta"] = real_delta

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
    # 💾 SAVE
    # =========================
    goal["progress"] = min(progress, target)
    goal["level"] = level

    data["goal"] = goal

    # ❗ ВАЖНО: НЕ ТРОГАЕМ prev_progress здесь
    # он обновится в следующем set_goal()

    # =========================
    # 📘 LOG
    # =========================
    data["log"].append(
        f"{goal['name']}: {goal['progress']}/{target} | level: {level} | trend: {trend} | state: {state} | delta: {data['last_delta']}"
    )

    return data
