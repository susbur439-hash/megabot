import os
import json

from core.module_router_v2 import ModuleRouterV2
from modules.brain_controller import decide
from core.log_manager import log_manager


# =========================================================
# 🧼 NORMALIZER
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

        except Exception:
            pass

        return {"task": text}

    return {"task": str(task)}


# =========================================================
# 🧠 BRAIN MAP
# =========================================================

def run_brain_map():

    import brain_map

    log_manager.log("\n🧠 BUILDING BRAIN MAP...\n")

    brain = brain_map.build_brain_map()

    brain_map.print_report(brain)

    with open("brain_map.json", "w", encoding="utf-8") as f:
        json.dump(brain, f, indent=2, ensure_ascii=False)

    log_manager.log("\n💾 Saved: brain_map.json")

    return {
        "status": "success",
        "files": brain["stats"]["total_files"]
    }


# =========================================================
# 🚀 ENTRY
# =========================================================

if __name__ == "__main__":

    # =========================
    # ⚙️ LOG MODE
    # =========================
    log_manager.set_mode("CLEAN")

    # =========================
    # 📥 INPUT
    # =========================
    raw_task = os.environ.get("TASK_JSON", "развивай себя")
    task = normalize(raw_task)

    log_manager.log("🚀 MEGABOT START")

    # =========================
    # 🧠 TASK TEXT
    # =========================
    task_text = str(task.get("task", "")).lower()

    # =========================
    # 🧠 SPECIAL: BRAIN MAP
    # =========================
    if any(x in task_text for x in [
        "brain map",
        "build graph",
        "scan repository"
    ]):
        result = run_brain_map()
        log_manager.log("✅ RESULT:", result)
        exit()

    # =========================
    # 🔌 ROUTER
    # =========================
    router = ModuleRouterV2()

    # =========================
    # 🧠 SPECIAL: ARCHITECTURE
    # =========================
    if any(x in task_text for x in [
        "architecture",
        "system roles",
        "router v2",
        "test router v2"
    ]):
        log_manager.log("\n🧠 ARCHITECTURE MODE\n")
        router.build_architecture_map()
        log_manager.log("✅ ARCHITECTURE READY")

    # =========================
    # 🧠 BRAIN DECISION
    # =========================
    decision = decide(task)

    log_manager.decision(decision)

    # =========================
    # 🛡 SAFETY CHECK
    # =========================
    module = decision.get("module")

    if module not in router.modules:

        log_manager.log(f"[WARN] Unknown module: {module}")
        log_manager.log("[FALLBACK] -> director")

        decision = {
            "module": "director",
            "data": task
        }

    # =========================
    # 🚀 EXECUTION
    # =========================
    result = router.route(decision)

    log_manager.log("✅ RESULT:", result)

    log_manager.log("\n🏁 MEGABOT END")
