def set_goal(data):
    # 🎯 если цели нет или она None — создаём
    if not data.get("goal"):
        data["goal"] = {
            "name": "improve_system",
            "progress": 0
        }

    return data


def update_goal(data):
    goal = data.get("goal")

    # 🔥 защита (на всякий случай)
    if not goal:
        goal = {
            "name": "improve_system",
            "progress": 0
        }

    evaluation = data.get("evaluation", {})
    score = evaluation.get("score", 50)

    # 📈 рост
    if score >= 70:
        goal["progress"] += 10

    elif score >= 40:
        goal["progress"] += 2

    else:
        goal["progress"] -= 5

    # 🔒 ограничения
    goal["progress"] = max(0, min(100, goal["progress"]))

    data["goal"] = goal

    data["log"].append(f"goal progress: {goal['progress']}%")

    return data
