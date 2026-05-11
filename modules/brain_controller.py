import json
import os

MEMORY_FILE = "code_understanding.json"


# =========================================================
# 📥 LOAD MEMORY
# =========================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        return {"error": str(e)}


# =========================================================
# 🧠 INTENT CLASSIFIER
# =========================================================

INTENTS = {

    "execution": [
        "run",
        "execute",
        "launch",
        "start",
        "build",
        "repair",
        "fix",
        "deploy",
        "create"
    ],

    "analysis": [
        "analyze",
        "scan",
        "inspect",
        "check",
        "review",
        "diagnose"
    ],

    "intelligence": [
        "brain",
        "system",
        "strategy",
        "architecture",
        "reason",
        "think"
    ]
}


# =========================================================
# 🧠 DETECT INTENT
# =========================================================

def detect_intent(task: str):

    task_lower = task.lower()

    scores = {}

    for intent, keywords in INTENTS.items():

        score = 0

        for word in keywords:

            if word in task_lower:
                score += 1

        scores[intent] = score

    best_intent = max(scores, key=scores.get)

    if scores[best_intent] == 0:
        return "unknown"

    return best_intent


# =========================================================
# 🧠 DECISION ENGINE
# =========================================================

def decide(task: str):

    memory = load_memory()

    summary = memory.get("summary", {})
    roles = summary.get("roles", {})

    intent = detect_intent(task)

    # =====================================================
    # ⚙ EXECUTION
    # =====================================================

    if intent == "execution":

        return {
            "module": "director",
            "data": {
                "task": task,
                "preferred": roles.get("execution_core", [])
            }
        }

    # =====================================================
    # 🔍 ANALYSIS
    # =====================================================

    if intent == "analysis":

        return {
            "module": "analysis",
            "data": {
                "task": task
            }
        }

    # =====================================================
    # 🧠 INTELLIGENCE
    # =====================================================

    if intent == "intelligence":

        return {
            "module": "intelligence_layer",
            "data": {
                "question": task,
                "brain_candidates": roles.get(
                    "decision_orchestrator", []
                )
            }
        }

    # =====================================================
    # ❓ UNKNOWN TASK
    # =====================================================

    return {
        "module": "task_interpreter",
        "data": {
            "task": task,
            "requires_analysis": True
        }
    }


# =========================================================
# 🚀 TEST LOOP
# =========================================================

if __name__ == "__main__":

    while True:

        task = input("\n🧠 Brain > ")

        if task in ["exit", "quit"]:
            break

        result = decide(task)

        print("\n🧠 DECISION:")
        print(json.dumps(result, indent=2))
