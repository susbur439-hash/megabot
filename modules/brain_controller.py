import json
import os

MEMORY_FILE = "code_understanding.json"


# =========================================================
# 📥 LOAD SYSTEM MEMORY
# =========================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return None

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


# =========================================================
# 🧠 DECISION ENGINE
# =========================================================

def decide(task: str):

    memory = load_memory()

    if not memory:
        return {
            "module": "director",
            "data": {"task": task}
        }

    summary = memory.get("summary", {})
    roles = summary.get("roles", {})

    task_lower = task.lower()

    # =====================================================
    # 🧠 INTELLIGENCE QUERY
    # =====================================================

    if "brain" in task_lower or "system" in task_lower:

        brain = roles.get("decision_orchestrator", [])

        return {
            "module": "intelligence_layer",
            "data": {
                "question": task,
                "brain_candidates": brain
            }
        }

    # =====================================================
    # ⚙ EXECUTION REQUEST
    # =====================================================

    if "run" in task_lower or "execute" in task_lower:

        execs = roles.get("execution_core", [])

        return {
            "module": "director",
            "data": {
                "task": task,
                "preferred": execs
            }
        }

    # =====================================================
    # 🔍 ANALYSIS REQUEST
    # =====================================================

    if "analyze" in task_lower or "scan" in task_lower:

        return {
            "module": "analysis",
            "data": {
                "task": task
            }
        }

    # =====================================================
    # 🧭 DEFAULT ROUTE
    # =====================================================

    return {
        "module": "director",
        "data": {
            "task": task
        }
    }


# =========================================================
# 🚀 ENTRY POINT (TEST)
# =========================================================

if __name__ == "__main__":

    while True:

        task = input("\n🧠 Brain > ")

        if task in ["exit", "quit"]:
            break

        decision = decide(task)

        print("\n🧠 DECISION:")
        print(decision)
