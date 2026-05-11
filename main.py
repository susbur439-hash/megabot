import os
import json

from core.module_router import ModuleRouter
from modules.brain_controller import decide


# =========================================================
# 🧼 NORMALIZER
# =========================================================
def normalize(task):

    # already dict
    if isinstance(task, dict):
        return task

    # string input
    if isinstance(task, str):

        text = task.strip()

        # try parse json
        try:

            parsed = json.loads(text)

            if isinstance(parsed, str):
                parsed = json.loads(parsed)

            if isinstance(parsed, dict):
                return parsed

        except:
            pass

        # clean text task
        return {
            "task": text
        }

    # fallback
    return {
        "task": str(task)
    }


# =========================================================
# 🚀 ENTRY
# =========================================================
if __name__ == "__main__":

    # =====================================================
    # 📥 INPUT
    # =====================================================
    raw_task = os.environ.get(
        "TASK_JSON",
        "развивай себя"
    )

    task = normalize(raw_task)

    print("🚀 MEGABOT START")
    print("🎯 NORMALIZED TASK:", task)

    # =====================================================
    # 🔌 ROUTER
    # =====================================================
    router = ModuleRouter()

    # =====================================================
    # 🧠 BRAIN
    # =====================================================
    decision = decide(task)

    print("[Brain Decision]:", decision)

    # =====================================================
    # 🛡 SAFETY LAYER
    # =====================================================
    module = decision.get("module")

    if module not in router.modules:

        print(
            f"[WARN] Unknown module: {module}"
        )

        print(
            "[FALLBACK] -> director"
        )

        decision = {
            "module": "director",
            "data": task
        }

    # =====================================================
    # 🚀 EXECUTION
    # =====================================================
    result = router.route(decision)

    print("✅ RESULT:", result)
