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
    # 🔥 DIRECT EXECUTION (.py FILE)
    # =========================
    if isinstance(task, str) and task.endswith(".py") and os.path.exists(task):
        print(f"🚀 Direct run: {task}")
        os.system(f"python {task}")
        exit(0)

    # =========================
    # 🔌 INIT ROUTER
    # =========================
    router = ModuleRouter()

    task_str = str(task).lower()

    # =========================
    # 🧠 ROUTING LOGIC (ВАЖНОЕ ИЗМЕНЕНИЕ)
    # =========================

    if "code_understanding" in task_str:
        command = {
            "module": "code_understanding",
            "data": {}
        }

    elif "list" in task_str:
        command = {
            "module": "system",
            "action": "list"
        }

    elif any(x in task_str for x in ["scan", "analyze", "system", "status"]):
        command = {
            "module": "analysis",
            "data": {"task": task}
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
