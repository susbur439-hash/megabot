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

    # 🛠 EXECUTION
    data = execution(data)

    # 🔥 СИНХРОНИЗАЦИЯ REAL DELTA
    if "evaluation" in data:
        if "last_delta" in data:
            data["evaluation"]["delta"] = data["last_delta"]

    # 📈 ОБНОВЛЕНИЕ ЦЕЛИ
    data = update_goal(data)

    return data


if __name__ == "__main__":
    task = "развивай себя"

    if len(sys.argv) > 1:
        task = sys.argv[1]

    print("🚀 Запуск задачи:", task)

    data = {
        "task": task,
        "analysis": None,
        "decision": None,
        "result": None,
        "evaluation": None,
        "goal": None,
        "log": [],
        "memory": []
    }

    # 🧠 ЛУЧШИЙ РЕЗУЛЬТАТ
    best_score = -1
    best_data = None

    for i in range(7):
        print(f"\n🔁 Цикл {i+1}")

        # 🔥 EXPLOIT / EXPLORE
        if best_data and random.random() < 0.7:
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

    print("\n✅ Задача завершена")
    print(f"🏁 Лучший результат за запуск: {best_score}")
