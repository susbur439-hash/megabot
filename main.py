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
    # 🔌 INIT ROUTER
    # =========================
    router = ModuleRouter()

    # =========================
    # 🧠 SIMPLE COMMAND BUILD
    # =========================
    if "list" in task.lower():
        command = {
            "module": "system",
            "action": "list"
        }
    else:
        command = {
            "module": "director",
            "data": {
                "task": task
            }
        }

    print("[Main] Command:", command)

    # =========================
    # 🚀 EXECUTION
    # =========================
    result = router.route(command)

    print("✅ RESULT:", result)
