import sys
import os
import time

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

    # 🔥 СИНХРОНИЗАЦИЯ РЕАЛЬНОГО DELTA
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

    for i in range(7):
        print(f"\n🔁 Цикл {i+1}")

        data = run_task(data)

        print("=== RESULT ===")
        print(data)

        time.sleep(1)

    print("\n✅ Задача завершена")
