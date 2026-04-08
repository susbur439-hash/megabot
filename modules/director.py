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

    # 🎯 GOAL
    data["last_layer"] = "goal"
    data = set_goal(data)

    # 🧠 ANALYSIS
    data["last_layer"] = "analysis"
    data = analysis(data)

    # 🧠 DECISION
    data["last_layer"] = "decision"
    data = decision(data)

    # 🔥 SELF IMPROVER
    data = self_improver(data)

    # =========================
    # 🧠 META-STRATEGY (FIX)
    # =========================

    score = data.get("evaluation", {}).get("score", 0)
    repeat = data.get("repeat_count", 0)

    if data.get("last_delta", 0) <= 0:
        strategy = "explore"
    elif data.get("force_explore"):
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
    # 🔥 ВАЖНО: НЕ ЛОМАЕМ decision
    # =========================

    # только мягкая корректировка
    if strategy == "explore":
        if data["decision"] == "run_module":
            data["decision"] = "create_module"

    elif strategy == "exploit":
        if data["decision"] == "create_module":
            data["decision"] = "run_module"

    elif strategy == "optimize":
        if data["decision"] == "create_module":
            data["decision"] = "improve_module"

    # ❗ ЖЁСТКИЙ АНТИ-БАГ
    if data.get("decision") == "generate_idea":
        data["decision"] = "create_module"
        data["log"].append("🔥 override: idea → create_module")

    # =========================
    # 🎭 MODE SYSTEM
    # =========================

    if strategy == "explore":
        mode = "aggressive"
    elif strategy == "exploit":
        mode = "balanced"
    elif strategy == "optimize":
        mode = "safe"
    else:
        mode = "balanced"

    data["mode"] = mode
    data["log"].append(f"mode: {mode}")

    # =========================
    # 🛑 ANTI-LOOP SYSTEM
    # =========================

    if "last_decision" in data:
        if data["decision"] == data["last_decision"]:
            data["repeat_count"] = data.get("repeat_count", 0) + 1

            penalty_step = -5 * data["repeat_count"]
            data["penalty"] = data.get("penalty", 0) + penalty_step

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
    # 🔥 SYNC
    # =========================

    if "evaluation" in data:
        before = data.get("goal", {}).get("history", [0])[-1] if data.get("goal", {}).get("history") else 0
        after = data.get("goal", {}).get("progress", 0)

        data["evaluation"]["delta"] = after - before

        if "penalty" in data:
            data["evaluation"]["score"] += data["penalty"]

            if data["evaluation"]["score"] < 0:
                data["evaluation"]["score"] = 0

            data["log"].append(f"penalty applied: {data['penalty']}")

    # =========================
    # 🎯 GOAL UPDATE
    # =========================

    data["last_layer"] = "goal_update"
    data = update_goal(data)

    return data


def analyze_experience(data):
    exp = data.get("experience", [])

    if not exp:
        return data

    best = max(exp, key=lambda x: x.get("score", 0))

    data["best_module"] = best
    data["log"].append(f"🏆 best module: {best['module']} ({best['score']})")

    return data


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
            "evaluation": {"score": 0, "delta": 0},
            "goal": None,
            "log": [],
            "memory": [],
            "experience": [],
            "repeat_count": 0,
            "force_explore": False,
            "penalty": 0
        }

        for i in range(10):
            print(f"\n🔁 Цикл {i+1}")

            data = analyze_experience(data)

            exploit_chance = 0.6

            if data.get("force_explore"):
                exploit_chance = 0.0
                print("🧪 FORCED EXPLORE")

            elif data.get("repeat_count", 0) >= 2:
                exploit_chance = 0.2

            elif best_score > 80:
                exploit_chance = 0.75

            if best_data and random.random() < exploit_chance:
                print("♻️ SMART EXPLOIT")

                best_copy = copy.deepcopy(best_data)

                data["experience"] = best_copy.get("experience", [])
                data["memory"] = best_copy.get("memory", [])
                data["best_module"] = best_copy.get("best_module")

                data["repeat_count"] = 0
                data["penalty"] = 0
                data["force_explore"] = False
                data["last_decision"] = None

            else:
                print("🧪 EXPLORE")

            data = run_task(data)

            current_score = data.get("evaluation", {}).get("score", 0)

            if best_data and current_score < best_score - 15:
                print("🛑 ДЕГРАДАЦИЯ → ОТКАТ")
                data = copy.deepcopy(best_data)
                continue

            if current_score > best_score:
                best_score = current_score
                best_data = copy.deepcopy(data)
                print(f"🏆 Новый лучший результат: {best_score}")

            print("=== RESULT ===")
            print(data)

            time.sleep(1)

    print("\n✅ Все задачи завершены")
    print(f"🏁 Лучший результат за запуск: {best_score}")
