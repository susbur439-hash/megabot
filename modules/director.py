import time
import copy
import random

from modules.analysis import analysis
from modules.decision import decision
from modules.execution import execution
from modules.goals import set_goal, update_goal
from modules.system_guard import system_guard
from modules.self_improver import self_improver
from modules.doctor import doctor
from modules.control_layer import ControlLayer  # 🔥 ДОБАВЛЕНО

# 👁 OBSERVER (отдельный модуль, НЕ авто)
try:
    from modules.system_observer import run as observer_run
except:
    observer_run = None


# 🧠 CONTROL LAYER INIT (ГЛОБАЛЬНЫЙ ПРЕДОХРАНИТЕЛЬ)
control_layer = ControlLayer()


def run_task(data):
    data.setdefault("log", [])

    # 🔥 START
    data["last_layer"] = "start"
    data = doctor(data)

    # GOAL
    data["last_layer"] = "goal"
    data = set_goal(data)

    # ANALYSIS
    data["last_layer"] = "analysis"
    data = analysis(data)

    # DECISION
    data["last_layer"] = "decision"
    data = decision(data)

    # SELF IMPROVE
    data = self_improver(data)

    best = data.get("best_module")

    # 🎯 БАЗОВОЕ РЕШЕНИЕ
    data["decision"] = "run_module" if best else "create_module"
    data["last_decision"] = data["decision"]

    # 🛑 CONTROL LAYER FILTER (НОВЫЙ КРИТИЧЕСКИЙ СЛОЙ)
    existing_modules = data.get("experience", [])
    existing_modules = [m.get("module") for m in existing_modules if isinstance(m, dict)]

    health = control_layer.check_system_health(existing_modules)

    decision_result = control_layer.filter_decision(data["decision"])

    if not decision_result["allowed"]:
        data["decision"] = decision_result["forced_decision"]
        data["log"].append("🛑 CONTROL OVERRIDE → " + data["decision"])

    # ⚡ BOOST
    data["boost"] = 1.2

    # 🚨 HARD SAFETY STOP (ЗАЩИТА ОТ СПАМА МОДУЛЕЙ)
    if data.get("decision") == "create_module":
        missing = control_layer.missing_core

        if len(missing) > 0:
            data["decision"] = "repair_core"
            data["log"].append("🚨 HARD BLOCK → repair_core: " + str(missing))

    # 🚀 EXECUTION
    data["last_layer"] = "execution"
    data = execution(data)

    data = system_guard(data)

    # GOAL UPDATE
    data["last_layer"] = "goal_update"
    data = update_goal(data)

    # POST ANALYSIS
    data["last_layer"] = "post_analysis"
    data = analysis(data)

    # 🧠 STRATEGY
    score = data.get("evaluation", {}).get("score", 0)
    last_delta = data.get("last_delta", 0)

    if last_delta <= 0:
        strategy = "explore"
    elif score >= 80:
        strategy = "exploit"
    elif score >= 50:
        strategy = "optimize"
    else:
        strategy = "explore"

    data["strategy"] = strategy

    # 🎯 КОРРЕКЦИЯ
    if strategy == "exploit" and best:
        data["decision"] = "run_module"
    elif strategy == "optimize" and best:
        data["decision"] = "improve_module"
    else:
        data["decision"] = "create_module"

    # 🎭 MODE
    data["mode"] = {
        "explore": "aggressive",
        "exploit": "balanced",
        "optimize": "safe"
    }[strategy]

    # 🛑 ANTI-LOOP
    if "prev_decision" in data:
        if data["decision"] == data["prev_decision"]:
            data["repeat_count"] = data.get("repeat_count", 0) + 1
        else:
            data["repeat_count"] = 0

    if data.get("repeat_count", 0) >= 3:
        data["decision"] = "create_module"
        data["repeat_count"] = 0

    data["prev_decision"] = data["decision"]

    # ⚡ FINAL BOOST
    data["boost"] = {
        "aggressive": 1.5,
        "balanced": 1.0,
        "safe": 0.7
    }[data["mode"]]

    # 🔥 END
    data["last_layer"] = "loop_end"
    data = doctor(data)

    # ✂️ ограничение лога
    data["log"] = data["log"][-200:]

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
        "repeat_count": 0,
        "run_observer": False
    }

    best_score = -1
    best_data = None

    max_cycles = 10

    for i in range(max_cycles):
        print(f"\n🔁 Цикл {i+1}")

        data = analyze_experience(data)

        if best_data and random.random() < 0.3:
            print("♻️ SMART EXPLOIT")
            data["best_module"] = best_data.get("best_module")
        else:
            print("🧪 EXPLORE")

        data = run_task(data)

        # 👁 OBSERVER
        if data.get("run_observer") and observer_run:
            print("👁 OBSERVER RUN")
            try:
                data = observer_run(data)
            except Exception as e:
                print("❌ observer error:", e)

            data["run_observer"] = False

        score = data.get("evaluation", {}).get("score", 0)

        if score > best_score:
            best_score = score
            best_data = copy.deepcopy(data)
            print(f"🏆 Новый лучший результат: {best_score}")

        print("=== RESULT ===")
        print(data)

        if data.get("goal", {}).get("progress", 0) >= 100:
            print("🎯 Цель достигнута — остановка")
            break

        time.sleep(1)

    print("\n🏁 Лучший результат:", best_score)
