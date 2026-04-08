import time
import copy
import random

from modules.analysis import analysis
from modules.decision import decision
from modules.execution import execution
from modules.goals import set_goal, update_goal
from modules.system_guard import system_guard
from modules.self_improver import self_improver


def run_task(data):
    data.setdefault("log", [])

    # =========================
    # GOAL
    # =========================
    data["last_layer"] = "goal"
    data = set_goal(data)

    # =========================
    # ANALYSIS
    # =========================
    data["last_layer"] = "analysis"
    data = analysis(data)

    # =========================
    # DECISION
    # =========================
    data["last_layer"] = "decision"
    data = decision(data)

    # =========================
    # SELF IMPROVE
    # =========================
    data = self_improver(data)

    score = data.get("evaluation", {}).get("score", 0)
    repeat = data.get("repeat_count", 0)
    last_delta = data.get("last_delta", 0)

    # =========================
    # 🧠 STRATEGY (СТАБИЛЬНАЯ)
    # =========================
    if last_delta <= 0:
        strategy = "explore"
    elif score >= 80:
        strategy = "exploit"
    elif score >= 50:
        strategy = "optimize"
    else:
        strategy = "explore"

    data["strategy"] = strategy
    data["log"].append(f"strategy: {strategy}")

    best = data.get("best_module")

    # =========================
    # 🎯 DECISION CONTROL (БЕЗ ХАОСА)
    # =========================
    if strategy == "exploit" and best:
        data["decision"] = "run_module"

    elif strategy == "optimize" and best:
        data["decision"] = "improve_module"

    else:
        data["decision"] = "create_module"

    # =========================
    # 🎭 MODE
    # =========================
    mode = {
        "explore": "aggressive",
        "exploit": "balanced",
        "optimize": "safe"
    }[strategy]

    data["mode"] = mode

    # =========================
    # 🛑 ANTI-LOOP
    # =========================
    if "last_decision" in data:
        if data["decision"] == data["last_decision"]:
            data["repeat_count"] = data.get("repeat_count", 0) + 1
        else:
            data["repeat_count"] = 0

    if data.get("repeat_count", 0) >= 3:
        data["decision"] = "create_module"
        data["log"].append("🧠 anti-loop → force create")
        data["repeat_count"] = 0

    data["last_decision"] = data["decision"]

    # =========================
    # ⚡ BOOST
    # =========================
    data["boost"] = {
        "aggressive": 1.5,
        "balanced": 1.0,
        "safe": 0.7
    }[mode]

    # =========================
    # 🚀 EXECUTION
    # =========================
    data["last_layer"] = "execution"
    data = execution(data)

    data = system_guard(data)

    # =========================
    # GOAL UPDATE
    # =========================
    data["last_layer"] = "goal_update"
    data = update_goal(data)

    return data


def analyze_experience(data):
    exp = data.get("experience", [])

    if not exp:
        return data

    best = max(exp, key=lambda x: x.get("score", 0))

    if not data.get("best_module") or best["score"] > data["best_module"].get("score", 0):
        data["best_module"] = best

    return data


def run(task):
    print("🚀 Запуск задачи:", task)

    data = {
        "task": task,
        "evaluation": {"score": 0, "delta": 0},
        "log": [],
        "memory": [],
        "experience": [],
        "repeat_count": 0
    }

    best_score = -1
    best_data = None

    for i in range(10):
        print(f"\n🔁 Цикл {i+1}")

        data = analyze_experience(data)

        # =========================
        # 🔥 SMART EXPLOIT (ФИКС)
        # =========================
        if best_data and random.random() < 0.3:
            print("♻️ SMART EXPLOIT")

            # ❗ ТОЛЬКО ЛУЧШИЙ МОДУЛЬ
            data["best_module"] = best_data.get("best_module")

        else:
            print("🧪 EXPLORE")

        data = run_task(data)

        score = data.get("evaluation", {}).get("score", 0)

        if score > best_score:
            best_score = score
            best_data = copy.deepcopy(data)
            print(f"🏆 Новый лучший результат: {best_score}")

        print("=== RESULT ===")
        print(data)

        time.sleep(1)

    print("\n🏁 Лучший результат:", best_score)
