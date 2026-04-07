# =========================
# 🎯 УСТАНОВКА ЦЕЛИ
# =========================
def set_goal(data):

    if "goal" not in data or not isinstance(data["goal"], dict):
        data["goal"] = {
            "name": "evolve_system",
            "progress": 0,
            "level": 1,
            "target": 100,
            "history": []
        }

    goal = data["goal"]

    # защита
    goal.setdefault("name", "evolve_system")
    goal.setdefault("progress", 0)
    goal.setdefault("level", 1)
    goal.setdefault("target", 100)
    goal.setdefault("history", [])

    return data


# =========================
# 📈 ОБНОВЛЕНИЕ ЦЕЛИ
# =========================
def update_goal(data):

    goal = data.get("goal", {})
    evaluation = data.get("evaluation", {})
    score = evaluation.get("score", 50)

    progress = goal.get("progress", 0)
    level = goal.get("level", 1)
    target = goal.get("target", 100)

    data.setdefault("log", [])

    # =========================
    # 🧠 ДИНАМИЧЕСКИЙ РОСТ
    # =========================

    if score >= 85:
        delta = 15
    elif score >= 70:
        delta = 10
    elif score >= 50:
        delta = 4
    elif score >= 30:
        delta = 1
    else:
        delta = -8

    progress += delta

    # =========================
    # 📊 ТРЕНД (важно)
    # =========================
    history = goal.get("history", [])
    history.append(score)
    history = history[-10:]  # последние 10

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
    # 🔥 УРОВНЕВАЯ СИСТЕМА
    # =========================
    if progress >= target:
        level += 1
        progress = 0

        data["log"].append(f"🚀 LEVEL UP → {level}")

        # 💥 усложнение
        goal["target"] = int(target * 1.2)  # каждый уровень сложнее
        data["difficulty"] = level

    elif progress < 0:
        progress = 0

    # =========================
    # 🧠 СОСТОЯНИЕ СИСТЕМЫ
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
    # 📦 СОХРАНЕНИЕ
    # =========================
    goal["progress"] = min(progress, target)
    goal["level"] = level

    data["goal"] = goal

    # =========================
    # 📘 ЛОГ
    # =========================
    data["log"].append(
        f"goal: {progress}/{target} | level: {level} | trend: {trend} | state: {state} | delta: {delta}"
    )

    return data
