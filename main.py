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

        except Exception:
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
# 🧠 SPECIAL TASKS
# =========================================================

def run_brain_map():

    import brain_map

    print("\n🧠 BUILDING BRAIN MAP...\n")

    brain = brain_map.build_brain_map()

    brain_map.print_report(brain)

    with open(
        "brain_map.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            brain,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n💾 Saved: brain_map.json")

    return {
        "status": "success",
        "brain_map_created": True,
        "files": brain["stats"]["total_files"]
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
    # 🧠 SPECIAL ROUTES
    # =====================================================

    task_text = str(
        task.get("task", "")
    ).lower()

    if (
        "brain map" in task_text
        or "build graph" in task_text
        or "scan repository" in task_text
    ):

        result = run_brain_map()

        print("\n✅ RESULT:", result)

        exit()

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
