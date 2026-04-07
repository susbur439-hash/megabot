import sys
import os
import time
import copy
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 🧠 MEGABOT CORE

from modules.analysis import analysis
from modules.decision import decision
from modules.execution import execution
from modules.goals import set_goal, update_goal


def run_task(data):
    # 🎯 УСТАНОВКА ЦЕЛИ
    data = set_goal(data)

    # 🔍 ANALYSIS
    data = analysis(data)

    # 🧠 DECISION
    data = decision(data)

    # 🛑 АНТИ-ЗАСТРЕВАНИЕ (умный штраф)
    if "last_decision" in data:
        if data["decision"] == data["last_decision"]:
            data["repeat_count"] = data.get("repeat_count", 0) + 1

            # увеличиваем штраф постепенно
            penalty_value = -5 * data["repeat_count"]
            data["penalty"] = penalty_value

            data["log"].append(f"⚠️ penalty: repeated decision x{data['repeat_count']}")

            # 🔥 ЖЕСТКИЙ СЛОМ ЗАЦИКЛИВАНИЯ
            if data["repeat_count"] >= 3:
                data["decision"] = "generate_idea"
                data["log"].append("🧠 forced switch: generate_idea")
        else:
            # сброс если сменилось поведение
            data["repeat_count"] = 0
            data["penalty"] = 0

    data["last_decision"] = data["decision"]

    # 🛠 EXECUTION
    data = execution(data)

    # 🔥 СИНХРОНИЗАЦИЯ REAL DELTA
    if "evaluation" in data:
        if "last_delta" in data:
            data["evaluation"]["delta"] = data["last_delta"]

        # 🔥 ПРИМЕНЕНИЕ ШТРАФА (но ограниченное)
        if "penalty" in data:
            data["evaluation"]["score"] += data["penalty"]

            # ограничение, чтобы не убить систему
            if data["evaluation"]["score"] < 0:
                data["evaluation"]["score"] = 0

            data["log"].append(f"penalty applied: {data['penalty']}")

    # 📈 ОБНОВЛЕНИЕ ЦЕЛИ
    data = update_goal(data)

    return data


if __name__ == "__main__":
    task = "развивай себя"

    if len(sys.argv) > 1:
        task = sys.argv[1]

    print("🚀 Запуск задачи:", task)

    # 🔥 MULTI-TASK РАЗДЕЛЕНИЕ
    tasks = [t.strip() for t in task.split(",")]

    # 🧠 ЛУЧШИЙ РЕЗУЛЬТАТ (глобально)
    best_score = -1
    best_data = None

    for t_index, single_task in enumerate(tasks):
        print(f"\n==============================")
        print(f"🎯 ЗАДАЧА {t_index+1}: {single_task}")
        print(f"==============================")

        data = {
            "task": single_task,
            "analysis": None,
            "decision": None,
            "result": None,
            "evaluation": None,
            "goal": None,
            "log": [],
            "memory": []
        }

        for i in range(7):
            print(f"\n🔁 Цикл {i+1}")

            # 🔥 ДИНАМИЧЕСКИЙ EXPLOIT / EXPLORE
            exploit_chance = 0.6

            # если застряли → уменьшаем exploit
            if data.get("repeat_count", 0) >= 2:
                exploit_chance = 0.2

            if best_data and random.random() < exploit_chance:
                print("♻️ Используем лучший найденный результат (exploit)")
                data = copy.deepcopy(best_data)

            data = run_task(data)

            # 📊 ТЕКУЩИЙ SCORE
            current_score = 0
            if data.get("evaluation"):
                current_score = data["evaluation"].get("score", 0)

            # 🏆 ОБНОВЛЕНИЕ ЛУЧШЕГО
            if current_score > best_score:
                best_score = current_score
                best_data = copy.deepcopy(data)
                print(f"🏆 Новый лучший результат: {best_score}")

            print("=== RESULT ===")
            print(data)

            time.sleep(1)

    print("\n✅ Все задачи завершены")
    print(f"🏁 Лучший результат за запуск: {best_score}")
