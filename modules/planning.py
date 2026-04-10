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

    # 📊 сохраняем историю
    goal["history"].append(progress)
    goal["history"] = goal["history"][-20:]

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

    return data
