import time
import copy
import random

from modules.analysis import analysis
from modules.decision import decision
from modules.execution import execution
from modules.goals import set_goal, update_goal
from modules.system_guard import system_guard
from modules.self_improver import self_improver


# =========================
# 🧠 CORE TASK PIPELINE
# =========================

def run_task(data):
    data.setdefault("log", [])

    # 🎯 GOAL
    data["last_layer"] = "goal"
    data = set_goal(data)

    # 🧠 ANALYSIS
    data["last_layer"] = "analysis"
    data = analysis(data)

    # 🧠 DECISION (ГЛАВНЫЙ)
    data["last_layer"] = "decision"
    data = decision(data)

    # 🔥 SELF IMPROVER
    data = self_improver(data)

    # =========================
    # 🧠 META-STRATEGY (НЕ ЛОМАЕТ decision)
    # =========================

    score = data.get("evaluation", {}).get("score", 0)
    repeat = data.get("repeat_count", 0)

    if data.get("last_delta", 0) <= 0:
        strategy = "explore"
    elif repeat >= 2:
        strategy = "explore"
    elif score > 85:
        strategy = "exploit"
    elif score < 50:
        strategy = "explore"
    else:
        strategy = "optimize"

    data["strategy"] = strategy
    data["log"].append(f"strategy: {strategy}")

    # =========================
    # 🔥 УМНЫЙ КОНТРОЛЬ decision
    # =========================

    best = data.get("best_module")

    if strategy == "exploit" and best:
        data["decision"] = "run_module"
        data["log"].append("🔥 override → run best module")

    elif strategy == "optimize" and best:
        if random.random() < 0.7:
            data["decision"] = "run_module"
        else:
            data["decision"] = "improve_module"

    elif strategy == "explore":
        # ❗ НЕ generate_idea!
        if not best:
            data["decision"] = "create_module"
        else:
            if random.random() < 0.5:
                data["decision"] = "create_module"
            else:
                data["decision"] = "run_module"

    # =========================
    # 🎭 MODE
    # =========================

    if strategy == "explore":
        mode = "aggressive"
    elif strategy == "exploit":
        mode = "balanced"
    else:
        mode = "safe"

    data["mode"] = mode
    data["log"].append(f"mode: {mode}")

    # =========================
    # 🛑 ANTI-LOOP
    # =========================

    if "last_decision" in data:
        if data["decision"] == data["last_decision"]:
            data["repeat_count"] = data.get("repeat_count", 0) + 1

            if data["repeat_count"] >= 3:
                data["decision"] = "improve_module"
                data["log"].append("🧠 anti-loop → force improve")

        else:
            data["repeat_count"] = 0

    data["last_decision"] = data["decision"]

    # =========================
    # ⚡ BOOST
    # =========================

    if mode == "aggressive":
        data["boost"] = 1.5
    elif mode == "safe":
        data["boost"] = 0.7
    else:
        data["boost"] = 1.0

    # =========================
    # 🛠 EXECUTION
    # =========================

    data["last_layer"] = "execution"
    data = execution(data)

    # =========================
    # 🛡 SYSTEM GUARD
    # =========================

    data = system_guard(data)

    # =========================
    # 🎯 GOAL UPDATE
    # =========================

    data["last_layer"] = "goal_update"
    data = update_goal(data)

    return data


# =========================
# 🧠 EXPERIENCE
# =========================

def analyze_experience(data):
    exp = data.get("experience", [])

    if not exp:
        return data

    best = max(exp, key=lambda x: x.get("score", 0))

    data["best_module"] = best
    data["log"].append(f"🏆 best module: {best['module']} ({best['score']})")

    return data


# =========================
# 🎛 DIRECTOR FINAL
# =========================

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

        # 🔥 УМНЫЙ EXPLOIT
        if best_data and random.random() < 0.6:
            print("♻️ SMART EXPLOIT")
            data = copy.deepcopy(best_data)
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
