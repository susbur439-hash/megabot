import time
import copy
import random

from modules.analysis import analysis
from modules.decision import decision
from modules.execution import execution
from modules.goals import set_goal, update_goal


# =========================
# 🧠 CORE TASK PIPELINE
# =========================

def run_task(data):
    data = set_goal(data)
    data = analysis(data)
    data = decision(data)

    # =========================
    # 🧠 META-STRATEGY
    # =========================

    if "strategy" not in data:
        data["strategy"] = "build"

    score = data.get("evaluation", {}).get("score", 0)
    repeat = data.get("repeat_count", 0)

    if data.get("force_explore"):
        data["strategy"] = "explore"

    elif repeat >= 2:
        data["strategy"] = "explore"

    elif score > 85:
        data["strategy"] = "exploit"

    elif score < 50:
        data["strategy"] = "build"

    else:
        data["strategy"] = "optimize"

    data["log"].append(f"strategy: {data['strategy']}")

    # 🎯 decision override
    if data["strategy"] == "explore":
        data["decision"] = "generate_idea"

    elif data["strategy"] == "exploit":
        data["decision"] = "run_module"

    elif data["strategy"] == "optimize":
        if data["decision"] == "add_module":
            data["decision"] = "improve_module"

    # =========================
    # 🎭 MODE
    # =========================

    if "mode" not in data:
        data["mode"] = "balanced"

    if data["strategy"] == "explore":
        data["mode"] = "aggressive"
    elif data["strategy"] == "exploit":
        data["mode"] = "balanced"
    elif data["strategy"] == "optimize":
        data["mode"] = "safe"

    data["log"].append(f"mode: {data['mode']}")

    # =========================
    # 🛑 ANTI-LOOP
    # =========================

    if "last_decision" in data:
        if data["decision"] == data["last_decision"]:
            data["repeat_count"] = data.get("repeat_count", 0) + 1

            penalty_step = -5 * data["repeat_count"]
            data["penalty"] += penalty_step

            data["log"].append(
                f"⚠️ repeat x{data['repeat_count']} (penalty {penalty_step})"
            )

            if data["repeat_count"] >= 3:
                data["force_explore"] = True
                data["log"].append("🧠 FORCE EXPLORE MODE")

        else:
            data["repeat_count"] = 0
            data["penalty"] = 0
            data["force_explore"] = False

    data["last_decision"] = data["decision"]

    # =========================
    # ⚡ MODE → BOOST
    # =========================

    if data["mode"] == "aggressive":
        data["boost"] = 1.5
    elif data["mode"] == "safe":
        data["boost"] = 0.7
    else:
        data["boost"] = 1.0

    # =========================
    # 🛠 EXECUTION
    # =========================

    data = execution(data)

    # =========================
    # 🔥 SYNC
    # =========================

    if "evaluation" in data:
        if "last_delta" in data:
            data["evaluation"]["delta"] = data["last_delta"]

        if "penalty" in data:
            data["evaluation"]["score"] += data["penalty"]

            if data["evaluation"]["score"] < 0:
                data["evaluation"]["score"] = 0

            data["log"].append(f"penalty applied: {data['penalty']}")

    data = update_goal(data)

    return data


# =========================
# 🎛 DIRECTOR
# =========================

def run(task):
    print("🚀 Запуск задачи:", task)

    tasks = [t.strip() for t in task.split(",")]

    best_score = -1
    best_data = None

    for t_index, single_task in enumerate(tasks):
        print("\n==============================")
        print(f"🎯 ЗАДАЧА {t_index+1}: {single_task}")
        print("==============================")

        data = {
            "task": single_task,
            "analysis": None,
            "decision": None,
            "result": None,
            "evaluation": None,
            "goal": None,
            "log": [],
            "memory": [],
            "repeat_count": 0,
            "force_explore": False,
            "penalty": 0
        }

        for i in range(7):
            print(f"\n🔁 Цикл {i+1}")

            exploit_chance = 0.6

            if data.get("force_explore"):
                exploit_chance = 0.0
                print("🧪 FORCED EXPLORE")

            elif data.get("repeat_count", 0) >= 2:
                exploit_chance = 0.2

            if best_data and random.random() < exploit_chance:
                print("♻️ SAFE EXPLOIT")

                best_copy = copy.deepcopy(best_data)

                data["experience"] = best_copy.get("experience", [])
                data["memory"] = best_copy.get("memory", [])

                data["repeat_count"] = 0
                data["penalty"] = 0
                data["force_explore"] = False
                data["last_decision"] = None

            else:
                print("🧪 EXPLORE")

            data = run_task(data)

            current_score = 0
            if data.get("evaluation"):
                current_score = data["evaluation"].get("score", 0)

            if current_score > best_score:
                best_score = current_score
                best_data = copy.deepcopy(data)
                print(f"🏆 Новый лучший результат: {best_score}")

            print("=== RESULT ===")
            print(data)

            time.sleep(1)

    print("\n✅ Все задачи завершены")
    print(f"🏁 Лучший результат за запуск: {best_score}")
