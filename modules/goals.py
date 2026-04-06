def set_goal(data):
    # 🎯 если цели нет — ставим
    if "goal" not in data:
        data["goal"] = {
            "name": "improve_system",
            "progress": 0
        }

    return data


def update_goal(data):
    goal = data.get("goal", {})
    evaluation = data.get("evaluation", {})

    score = evaluation.get("score", 50)

    # 📈 если хорошо → растём
    if score >= 70:
        goal["progress"] += 10

    # ⚠️ если средне → немного растём
    elif score >= 40:
        goal["progress"] += 2

    # ❌ если плохо → откат
    else:
        goal["progress"] -= 5

    # 🔒 ограничения
    goal["progress"] = max(0, min(100, goal["progress"]))

    data["goal"] = goal

    data["log"].append(f"goal progress: {goal['progress']}%")

    return data
