import os
import json
from core.module_router import ModuleRouter


if __name__ == "__main__":

    # =========================
    # 📥 TASK FROM CONTROL PANEL
    # =========================
    task = os.environ.get("TASK_JSON", "развивай себя")

    try:
        parsed = json.loads(task)
        if isinstance(parsed, dict) and "task" in parsed:
            task = parsed["task"]
    except:
        pass

    print("🚀 MEGABOT START")
    print("🎯 TASK:", task)

    # =========================
    # 🔥 DIRECT EXECUTION (КЛЮЧЕВОЕ!)
    # =========================
    if isinstance(task, str) and task.endswith(".py") and os.path.exists(task):
        print(f"🚀 Direct run: {task}")
        os.system(f"python {task}")
        exit(0)

    # =========================
    # 🔌 INIT ROUTER
    # =========================
    router = ModuleRouter()

    # =========================
    # 🧠 SAFE TASK STRING
    # =========================
    task_str = task if isinstance(task, str) else str(task)

    # =========================
    # 🧠 SIMPLE COMMAND BUILD
    # =========================
    if "list" in task_str.lower():
        command = {
            "module": "system",
            "action": "list"
        }
    else:
        command = {
            "module": "director",
            "data": {
                "task": task_str
            }
        }

    print("[Main] Command:", command)

    # =========================
    # 🚀 EXECUTION
    # =========================
    result = router.route(command)

    print("✅ RESULT:", result)
