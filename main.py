import os
import json
from core.module_router import ModuleRouter
from modules.brain_controller import decide


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

        if cleaned.startswith("python "):

            script_path = cleaned.replace("python ", "", 1).strip()

            if os.path.exists(script_path):
                print(f"🚀 Direct run: {script_path}")
                os.system(f"python {script_path}")
                exit(0)

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
    # 🧠 BRAIN LAYER (НОВОЕ)
    # =========================
    decision = decide(str(task))

    print("[Brain Decision]:", decision)

    # =========================
    # 🚀 EXECUTION
    # =========================
    result = router.route(decision)

    print("✅ RESULT:", result)
