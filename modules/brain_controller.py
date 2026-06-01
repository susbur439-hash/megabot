import json
import os

from core.system_state import system_state
from core.system_brain_bridge import SystemBrainBridge

MEMORY_FILE = "code_understanding.json"

# =========================
# 🧠 SINGLETON BRIDGE
# =========================
bridge = SystemBrainBridge()


def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        return {"error": str(e)}


# =========================
# 🧠 INTENT CLASSIFIER
# =========================
INTENTS = {
    "execution": ["run", "execute", "launch", "start", "build", "repair", "fix", "deploy", "create"],
    "analysis": ["analyze", "scan", "inspect", "check", "review", "diagnose"],
    "intelligence": ["brain", "system", "strategy", "architecture", "reason", "think"]
}


def detect_intent(task_text):

    task_lower = task_text.lower()
    scores = {}

    for intent, keywords in INTENTS.items():
        scores[intent] = sum(1 for w in keywords if w in task_lower)

    best = max(scores, key=scores.get)

    return best if scores[best] > 0 else "unknown"


# =========================
# 🧠 DECISION ENGINE
# =========================
def decide(task):

    # FIX 1: load first, inject second (логика состояния)
    state = system_state.load()

    if isinstance(task, dict):
        task_text = task.get("task", "")
    else:
        task_text = str(task)

    state = system_state.inject(task_text)

    # FIX 2: reuse single bridge (НЕ пересоздаём)
    roles = bridge.roles
    bridge.refresh()

    intent = detect_intent(task_text)

    state["intent"] = intent
    state["task_text"] = task_text

    execution_pool = roles.get("EXECUTION", [])
    analysis_pool = roles.get("ANALYSIS", [])
    decision_pool = roles.get("DECISION", [])

    # =========================
    # EXECUTION
    # =========================
    if intent == "execution":

        return {
            "module": bridge.get_execution_module(),
            "data": {
                "task": task_text,
                "system_state": state,
                "execution_pool": execution_pool
            }
        }

    # =========================
    # ANALYSIS
    # =========================
    if intent == "analysis":

        return {
            "module": bridge.get_analysis_module(),
            "data": {
                "task": task_text,
                "system_state": state,
                "analysis_pool": analysis_pool
            }
        }

    # =========================
    # INTELLIGENCE
    # =========================
    if intent == "intelligence":

        return {
            "module": bridge.get_decision_module(),
            "data": {
                "question": task_text,
                "system_state": state,
                "decision_pool": decision_pool
            }
        }

    # =========================
    # UNKNOWN
    # =========================
    return {
        "module": "task_interpreter",
        "data": {
            "task": task_text,
            "requires_analysis": True,
            "system_state": state
        }
    }


# =========================
# 🚀 TEST LOOP
# =========================
if __name__ == "__main__":

    while True:

        task = input("\n🧠 Brain > ")

        if task in ["exit", "quit"]:
            break

        result = decide(task)

        print("\n🧠 DECISION:")
        print(json.dumps(result, indent=2, ensure_ascii=False))