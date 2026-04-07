def set_goal(data):

    if "goal" not in data or not isinstance(data["goal"], dict):
        data["goal"] = {}

    goal = data["goal"]

    # 🔥 убрали жёсткую привязку имени
    goal.setdefault("name", data.get("task_type", "adaptive_goal"))
    goal.setdefault("progress", 0)
    goal.setdefault("level", 1)
    goal.setdefault("target", 100)
    goal.setdefault("history", [])

    return data


def update_goal(data):

    goal = data.get("goal", {})
    evaluation = data.get("evaluation", {})
    score = evaluation.get("score", 50)

    progress = goal.get("progress", 0)
    level = goal.get("level", 1)
    target = goal.get("target", 100)

    data.setdefault("log", [])

    # =========================
    # 🔥 ОСНОВА = РЕАЛЬНЫЙ DELTA (фикс)
    # =========================
    real_delta = data.get("last_delta", 0)

    # 🔥 НЕ пересчитываем сильно — только корректируем
    if score >= 85:
        delta = real_delta + 2
    elif score >= 70:
        delta = real_delta + 1
    elif score >= 50:
        delta = real_delta
    elif score >= 30:
        delta = real_delta - 1
    else:
        delta = real_delta - 3

    progress += delta

    # =========================
    # 📊 ТРЕНД
    # =========================
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
    # 🔥 LEVEL SYSTEM (фикс)
    # =========================
    if progress >= target:
        level += 1

        # ✅ сохраняем остаток (а не обнуляем)
        progress = progress - target

        data["log"].append(f"🚀 LEVEL UP → {level}")

        target = int(target * 1.2)
        goal["target"] = target
        data["difficulty"] = level

    elif progress < 0:
        progress = 0

    # =========================
    # 🧠 STATE
    # =========================
    if trend == "down":
        state = "crisis"
    elif trend == "up" and score > 80:
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

    # =========================
    # 📘 LOG (фикс имени)
    # =========================
    data["log"].append(
        f"{goal['name']}: {goal['progress']}/{target} | level: {level} | trend: {trend} | state: {state} | delta: {delta} | real: {real_delta}"
    )

    return data
