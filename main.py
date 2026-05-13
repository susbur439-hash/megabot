import os
import json

from core.module_router_v2 import ModuleRouterV2
from modules.brain_controller import decide


# =========================================================
# 🧼 NORMALIZER
# =========================================================

def normalize(task):

    # =========================
    # 📦 ALREADY DICT
    # =========================

    if isinstance(task, dict):
        return task

    # =========================
    # 📝 STRING INPUT
    # =========================

    if isinstance(task, str):

        text = task.strip()

        # =====================
        # 🔍 TRY JSON
        # =====================

        try:

            parsed = json.loads(text)

            if isinstance(parsed, str):
                parsed = json.loads(parsed)

            if isinstance(parsed, dict):
                return parsed

        except Exception:
            pass

        # =====================
        # 🧠 CLEAN TASK
        # =====================

        return {
            "task": text
        }

    # =========================
    # ❌ FALLBACK
    # =========================

    return {
        "task": str(task)
    }


# =========================================================
# 🧠 BRAIN MAP
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
# 🧠 ARCHITECTURE MAP
# =========================================================

def show_architecture(router):

    print("\n🧠 SYSTEM ARCHITECTURE")
    print("=" * 50)

    roles = router.roles

    for role, modules in roles.items():

        print(f"\n[{role}] ({len(modules)})")

        for m in modules[:10]:
            print(f"  - {m}")

    print("\n🔁 FLOW:")
    print(" → ".join(router.get_flow()))

    return {
        "roles": dict(roles),
        "flow": router.get_flow()
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
    # 🧠 TASK TEXT
    # =====================================================

    task_text = str(
        task.get("task", "")
    ).lower()

    # =====================================================
    # 🧠 SPECIAL: BRAIN MAP
    # =====================================================

    if (
        "brain map" in task_text
        or "build graph" in task_text
        or "scan repository" in task_text
    ):

        result = run_brain_map()

        print("\n✅ RESULT:", result)

        exit()

    # =====================================================
    # 🔌 ROUTER V2
    # =====================================================

    router = ModuleRouterV2()

    # =====================================================
    # 🧠 SPECIAL: ARCHITECTURE
    # =====================================================

    if (
        "architecture" in task_text
        or "system roles" in task_text
        or "router v2" in task_text
        or "test router v2" in task_text
    ):

        result = show_architecture(router)

        print("\n✅ ARCHITECTURE READY")

    # =====================================================
    # 🧠 BRAIN
    # =====================================================

    decision = decide(task)

    print("[Brain Decision]:", decision)

    # =====================================================
    # 🛡 SAFETY
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

    print("\n🏁 MEGABOT END")
