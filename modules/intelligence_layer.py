# =========================================================
# 🧠 MEGABOT INTELLIGENCE LAYER v1
# 🧠 QUERY + REASONING OVER code_understanding.json
# =========================================================

import json
import os
import sys

MEMORY_FILE = "code_understanding.json"


# =========================
# 📥 LOAD MEMORY
# =========================
def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return None

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


# =========================
# 🧠 FIND ROLE FILES
# =========================
def find_by_role(memory, role):

    result = []
    files = memory.get("files", {})

    for f, data in files.items():
        if data.get("role") == role:
            result.append(f)

    return result


# =========================
# 🧠 SEARCH FILES
# =========================
def search_files(memory, keyword):

    result = []
    files = memory.get("files", {})

    for f, data in files.items():
        if keyword.lower() in f.lower():
            result.append(f)

    return result


# =========================
# 🧠 MAIN ENGINE
# =========================
def query(question: str):

    memory = load_memory()

    if not memory:
        return {"error": "memory not found"}

    q = question.lower()

    # brain
    if "brain" in q or "director" in q:
        return {
            "answer": "Main brain candidates",
            "files": find_by_role(memory, "decision_orchestrator")
        }

    # execution
    if "execution" in q or "engine" in q:
        return {
            "answer": "Execution core modules",
            "files": find_by_role(memory, "execution_core")
        }

    # control
    if "control" in q:
        return {
            "answer": "Control layer modules",
            "files": find_by_role(memory, "control_layer")
        }

    # search
    if "module" in q or "file" in q:
        return {
            "answer": "Search result",
            "files": search_files(memory, q)
        }

    # summary
    if "summary" in q or "system" in q:
        return memory.get("summary", {})

    return {
        "answer": "I don't understand query yet",
        "hint": [
            "brain",
            "execution",
            "control",
            "system summary"
        ]
    }


# =========================
# 🔌 ROUTER COMPATIBILITY FIX
# =========================
def run(data):

    """
    Это ОБЯЗАТЕЛЬНО для ModuleRouter.
    Router вызывает module.run(data)
    """

    # поддержка разных входов
    if isinstance(data, dict):
        question = data.get("question") or data.get("task") or str(data)
    else:
        question = str(data)

    return {
        "status": "ok",
        "module": "intelligence_layer",
        "result": query(question)
    }


# =========================
# ▶ ENTRY POINT
# =========================
if __name__ == "__main__":

    # CI / GitHub MODE
    if len(sys.argv) > 1:

        question = " ".join(sys.argv[1:])
        result = query(question)

        print("\n📊 RESULT:\n")
        print(result)

    # LOCAL MODE (без падений в CI)
    else:

        print("🧠 Megabot Intelligence Layer (local mode)")
        print("Type 'exit' to quit")

        while True:

            try:
                q = input("\n🧠 Ask Megabot > ")

                if q.lower() in ["exit", "quit"]:
                    break

                print(query(q))

            except EOFError:
                break
