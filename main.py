import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 🧠 MEGABOT CORE

from modules.analysis import analysis
from modules.decision import decision
from modules.action import action
from modules.execution import execution
from modules.goals import set_goal, update_goal  # 🔥 НОВОЕ


def run_task(data):
    # 🎯 УСТАНОВКА ЦЕЛИ
    data = set_goal(data)

    # 🔍 ANALYSIS
    data = analysis(data)

    # 🧠 DECISION
    data = decision(data)

    # ⚡ ACTION
    data = action(data)

    # 🛠 EXECUTION
    data = execution(data)

    # 📈 ОБНОВЛЕНИЕ ЦЕЛИ
    data = update_goal(data)

    return data


if __name__ == "__main__":
    # 🔥 Получаем задачу из GitHub Actions
    task = "развивай себя"

    if len(sys.argv) > 1:
        task = sys.argv[1]

    print("🚀 Запуск задачи:", task)

    # 🔥 ГЛАВНЫЙ DATA-БЛОК
    data = {
        "task": task,
        "analysis": None,
        "decision": None,
        "result": None,
        "evaluation": None,
        "goal": None,  # 🔥 НОВОЕ
        "log": [],
        "memory": []
    }

    # 🔁 ЦИКЛ
    for i in range(7):
        print(f"\n🔁 Цикл {i+1}")

        data = run_task(data)

        print("=== RESULT ===")
        print(data)

        time.sleep(1)

    print("\n✅ Задача завершена")
