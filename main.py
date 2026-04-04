import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 🧠 MEGABOT CORE

from modules.analysis import analysis
from modules.decision import decision
from modules.action import action
from modules.execution import execution


def run_task(data):
    # 🔍 ANALYSIS
    data = analysis(data)

    # 🧠 DECISION
    data = decision(data)

    # ⚡ ACTION
    data = action(data)

    # 🛠 EXECUTION
    data = execution(data)

    return data


if __name__ == "__main__":
    data = {
        "task": "развивай себя",
        "analysis": None,
        "decision": None,
        "result": None,
        "log": [],
        "memory": []  # 🧠 ВОТ ЭТО ГЛАВНОЕ
    }

    for i in range(5):
        data = run_task(data)

        print("=== RESULT ===")
        print(data)

        time.sleep(1)
