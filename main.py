import os
import json
from core.module_router import ModuleRouter
from modules.brain_controller import decide


# =========================================================
# 🧼 NORMALIZER (СТАБИЛИЗАЦИЯ ВХОДА)
# =========================================================
def normalize(task):

    if isinstance(task, dict):
        return task

    if isinstance(task, str):

        text = task.strip()

        try:
            parsed = json.loads(text)

            if isinstance(parsed, str):
                parsed = json.loads(parsed)

            if isinstance(parsed, dict):
                return parsed

        except:
            pass

        return {
            "module": "analysis",
            "data": {
                "task": text
            }
        }

    return {
        "module": "analysis",
        "data": {"task": str(task)}
    }


# =========================================================
# 🚀 ENTRY POINT
# =========================================================
if __name__ == "__main__":

    # =========================
    # 📥 TASK
    # =========================
    task = os.environ.get("TASK_JSON", "развивай себя")

    task = normalize(task)

    print("🚀 MEGABOT START")
    print("🎯 TASK:", task)

    # =========================
    # 🔥 DIRECT EXECUTION
    # =========================
    if isinstance(task, dict):

        cleaned = str(task.get("data", {}).get("task", "")).strip()

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
    # 🔌 ROUTER
    # =========================
    router = ModuleRouter()

    # =========================
    # 🧠 BRAIN DECISION
    # =========================
    decision = decide(str(task.get("data", {}).get("task", "")))

    print("[Brain Decision]:", decision)

    # =========================
    # 🧠 SAFETY LAYER (ЖЁСТКАЯ ЗАЩИТА)
    # =========================
    module = decision.get("module")

    if module not in router.modules:

        print(f"[WARN] Brain selected unknown module: {module}")
        print("[FALLBACK] switching to director")

        decision = {
            "module": "director",
            "data": task.get("data", {})
        }

    # =========================
    # 🚀 EXECUTION
    # =========================
    result = router.route(decision)

    print("✅ RESULT:", result)
