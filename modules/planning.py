import random


# =========================
# 🎯 GOAL MANAGER
# =========================
def update_goal(data):
    goal = data.setdefault("goal", {})
    goal.setdefault("name", "adaptive_goal")
    goal.setdefault("progress", 0)
    goal.setdefault("target", 100)
    goal.setdefault("level", 1)
    goal.setdefault("history", [])

    progress = goal["progress"]
    target = goal["target"]

    # 🧠 если цель достигнута — повышаем уровень
    if progress >= target:
        goal["level"] += 1
        goal["progress"] = 0
        goal["target"] = int(target * 1.2)

        data["log"].append(f"🎯 LEVEL UP → {goal['level']}")

    return data


# =========================
# 📊 ANALYZE STATE
# =========================
def analyze_state(data):
    env = data.get("env", {})
    goal = data.get("goal", {})

    state = {}

    # 📉 стагнация
    history = goal.get("history", [])
    if len(history) >= 3:
        state["stagnation"] = history[-1] <= history[-2] <= history[-3]
    else:
        state["stagnation"] = False

    # 📈 тренд
    if len(history) >= 2:
        if history[-1] > history[-2]:
            state["trend"] = "up"
        elif history[-1] < history[-2]:
            state["trend"] = "down"
        else:
            state["trend"] = "stable"
    else:
        state["trend"] = "stable"

    # ⚡ энергия
    state["energy"] = env.get("energy", 100)

    return state


# =========================
# 🧠 PLANNING
# =========================
def make_plan(data, state):
    task = data.get("task", "").lower()

    plan = []

    # 🎯 если задача про файлы
    if "файл" in task:
        plan.append("create_file")

    # 🧠 если задача про развитие
    if "развивай" in task or "develop" in task:
        plan.append("create_module")
        plan.append("improve")

    # 📉 если стагнация — исследуем
    if state.get("stagnation"):
        plan.append("explore")

    # 📈 если рост — усиливаем
    if state.get("trend") == "up":
        plan.append("exploit")

    # ⚡ если мало энергии — экономим
    if state.get("energy", 100) < 30:
        plan = ["light_action"]

    # fallback
    if not plan:
        plan = ["explore"]

    return plan


# =========================
# 🎬 APPLY PLAN
# =========================
def apply_plan(data, plan):
    data["plan"] = plan

    if not plan:
        data["strategy"] = "explore"
        return data

    main = plan[0]

    if main == "create_file":
        data["strategy"] = "force_file"

    elif main == "create_module":
        data["strategy"] = "build_module"

    elif main == "improve":
        data["strategy"] = "optimize"

    elif main == "explore":
        data["strategy"] = "explore"

    elif main == "exploit":
        data["strategy"] = "exploit"

    elif main == "light_action":
        data["strategy"] = "light"

    else:
        data["strategy"] = "explore"

    data["log"].append(f"🧠 plan: {plan} | strategy: {data['strategy']}")

    return data


# =========================
# 🎯 APPLY RESULT (REWARD)
# =========================
def apply_result(data):
    goal = data.get("goal", {})
    strategy = data.get("strategy", "explore")

    progress_gain = 0

    # 🎲 базовая логика награды
    if strategy == "explore":
        progress_gain = random.randint(1, 5)

    elif strategy == "exploit":
        progress_gain = random.randint(5, 10)

    elif strategy == "build_module":
        progress_gain = random.randint(3, 8)

    elif strategy == "optimize":
        progress_gain = random.randint(2, 6)

    elif strategy == "force_file":
        progress_gain = random.randint(1, 4)

    elif strategy == "light":
        progress_gain = 1

    # 📈 применяем
    goal["progress"] += progress_gain

    data["log"].append(f"📈 progress +{progress_gain} → {goal['progress']}")

    return data


# =========================
# 📝 UPDATE HISTORY
# =========================
def update_history(data):
    goal = data.get("goal", {})
    history = goal.setdefault("history", [])

    history.append(goal.get("progress", 0))
    goal["history"] = history[-20:]

    return data


# =========================
# 🚀 MAIN ENTRY
# =========================
def run(data):

    data.setdefault("log", [])

    # 🎯 goal update
    data = update_goal(data)

    # 📊 анализ состояния
    state = analyze_state(data)

    # 🧠 планирование
    plan = make_plan(data, state)

    # 🎬 применяем план
    data = apply_plan(data, plan)

    # 🚀 результат действия
    data = apply_result(data)

    # 📝 обновляем историю (ПОСЛЕ результата)
    data = update_history(data)

    return data
