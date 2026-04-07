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

    # 🛑 АНТИ-ЗАСТРЕВАНИЕ (умный)
    if "last_decision" in data:
        if data["decision"] == data["last_decision"]:
            data["repeat_count"] = data.get("repeat_count", 0) + 1

            penalty_value = -5 * data["repeat_count"]
            data["penalty"] = penalty_value

            data["log"].append(f"⚠️ repeat x{data['repeat_count']}")

            # 🔥 НЕ ломаем decision, а даем сигнал системе
            if data["repeat_count"] >= 3:
                data["force_explore"] = True
                data["log"].append("🧪 force explore mode")
        else:
            data["repeat_count"] = 0
            data["penalty"] = 0

    data["last_decision"] = data["decision"]

    # 🛠 EXECUTION
    data = execution(data)

    # 🔥 СИНХРОНИЗАЦИЯ
    if "evaluation" in data:
        if "last_delta" in data:
            data["evaluation"]["delta"] = data["last_delta"]

        if "penalty" in data:
            data["evaluation"]["score"] += data["penalty"]

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

    tasks = [t.strip() for t in task.split(",")]

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
            "memory": [],
            "repeat_count": 0,
            "force_explore": False
        }

        for i in range(7):
            print(f"\n🔁 Цикл {i+1}")

            exploit_chance = 0.6

            # 🔥 если застряли → режем exploit
            if data.get("repeat_count", 0) >= 2:
                exploit_chance = 0.2

            if best_data:
                if data.get("force_explore"):
                    print("🧪 Принудительное исследование")
                    data["force_explore"] = False

                elif random.random() < exploit_chance:
                    print("♻️ Частичный exploit")

                    best_copy = copy.deepcopy(best_data)

                    # ❗ копируем только опыт (а не всё состояние)
                    data["experience"] = best_copy.get("experience", [])
                    data["memory"] = best_copy.get("memory", [])

                else:
                    print("🧪 Исследование")

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
