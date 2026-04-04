
# 🧠 MEGABOT CORE

from modules.analysis import analysis
from modules.decision import decision
from modules.action import action
from modules.execution import execution

def run_task(task_text):
    data = {
        "task": task_text,
        "analysis": None,
        "decision": None,
        "result": None,
        "log": []
    }

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
    task = "развивай себя"

    while True:
        result = run_task(task)

        print("=== RESULT ===")
        print(result)

        input("Нажми Enter для следующего цикла...")
