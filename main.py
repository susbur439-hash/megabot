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
    # 🔥 DIRECT EXECUTION
    # =========================
    if isinstance(task, str):

        cleaned = task.strip()

        # ---------------------------------
        # python some_script.py
        # ---------------------------------
        if cleaned.startswith("python "):

            script_path = cleaned.replace(
                "python ",
                "",
                1
            ).strip()

            if os.path.exists(script_path):

                print(f"🚀 Direct run: {script_path}")

                os.system(f"python {script_path}")

                exit(0)

        # ---------------------------------
        # direct some_script.py
        # ---------------------------------
        elif cleaned.endswith(".py"):

            if os.path.exists(cleaned):

                print(f"🚀 Direct run: {cleaned}")

                os.system(f"python {cleaned}")

                exit(0)

    # =========================
    # 🔌 INIT ROUTER
    # =========================
    router = ModuleRouter()

    # =========================
    # 🧠 SAFE TASK STRING
    # =========================
    task_str = str(task).lower()

    # =========================
    # 🧠 ROUTING LOGIC
    # =========================

    if "list" in task_str:

        command = {
            "module": "system",
            "action": "list"
        }

    elif any(
        x in task_str
        for x in [
            "scan",
            "analyze",
            "system",
            "status"
        ]
    ):

        command = {
            "module": "analysis",
            "data": {
                "task": task
            }
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
