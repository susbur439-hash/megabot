import os

# 📁 создаём папку modules
os.makedirs("modules", exist_ok=True)

# 📄 файлы и их содержимое
files = {
    "main.py": '''from modules.analysis import analysis
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

    data = analysis(data)
    data = decision(data)
    data = action(data)
    data = execution(data)

    return data

if __name__ == "__main__":
    result = run_task("развивай себя")
    print(result)
''',

    "modules/analysis.py": '''def analysis(data):
    task = data["task"]

    if "развивай" in task:
        data["analysis"] = "self_development"
    else:
        data["analysis"] = "unknown"

    data["log"].append("analysis done")
    return data
''',

    "modules/decision.py": '''def decision(data):
    if data["analysis"] == "self_development":
        data["decision"] = "add_module"
    else:
        data["decision"] = "do_nothing"

    data["log"].append("decision made")
    return data
''',

    "modules/action.py": '''def action(data):
    if data["decision"] == "add_module":
        data["result"] = "System wants to add a new module"
    else:
        data["result"] = "No action"

    data["log"].append("action selected")
    return data
''',

    "modules/execution.py": '''def execution(data):
    print("EXECUTION:", data["result"])
    data["log"].append("execution complete")
    return data
'''
}

# 🛠 создаём файлы
for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Структура создана!")
