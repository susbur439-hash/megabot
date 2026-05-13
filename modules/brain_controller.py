import json
import os

from core.system_state import system_state

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
        "run", "execute", "launch", "start",
        "build", "repair", "fix", "deploy", "create"
    ],

    "analysis": [
        "analyze", "scan", "inspect", "check",
        "review", "diagnose"
    ],

    "intelligence": [
        "brain", "system", "strategy",
        "architecture", "reason", "think"
    ]
}


# =========================================================
# 🧠 DETECT INTENT
# =========================================================

def detect_intent(task_text):

    task_lower = task_text.lower()

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
# 🧠 DECISION ENGINE (STATE-BASED)
# =========================================================

def decide(task):

    # =========================
    # 🧠 SYSTEM STATE INTEGRATION
    # =========================
    state = system_state.inject(task)
    state = system_state.load()

    # нормализация
    if isinstance(task, dict):
        task_text = task.get("task", "")
    else:
        task_text = str(task)

    memory = load_memory()

    summary = memory.get("summary", {})
    roles = summary.get("roles", {})

    intent = detect_intent(task_text)

    # сохраняем в state
    state["intent"] = intent
    state["task_text"] = task_text

    # =====================================================
    # ⚙ EXECUTION
    # =====================================================

    if intent == "execution":

        return {
            "module": "director",
            "data": {
                "task": task_text,
                "preferred": roles.get("execution_core", []),
                "system_state": state
            }
        }

    # =====================================================
    # 🔍 ANALYSIS
    # =====================================================

    if intent == "analysis":

        return {
            "module": "analysis",
            "data": {
                "task": task_text,
                "system_state": state
            }
        }

    # =====================================================
    # 🧠 INTELLIGENCE
    # =====================================================

    if intent == "intelligence":

        return {
            "module": "intelligence_layer",
            "data": {
                "question": task_text,
                "brain_candidates": roles.get("decision_orchestrator", []),
                "system_state": state
            }
        }

    # =====================================================
    # ❓ UNKNOWN TASK
    # =====================================================

    return {
        "module": "task_interpreter",
        "data": {
            "task": task_text,
            "requires_analysis": True,
            "system_state": state
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
        print(json.dumps(result, indent=2, ensure_ascii=False))
