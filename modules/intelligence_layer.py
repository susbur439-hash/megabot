# =========================================================
# 🧠 MEGABOT INTELLIGENCE LAYER v1
# 🧠 QUERY + REASONING OVER code_understanding.json
# =========================================================

import json
import os

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
# 🧠 FIND MODULES BY KEYWORD
# =========================
def search_files(memory, keyword):

    result = []
    files = memory.get("files", {})

    for f, data in files.items():

        if keyword.lower() in f.lower():
            result.append(f)

    return result


# =========================
# 🧠 MAIN INTELLIGENCE ENGINE
# =========================
def query(question: str):

    memory = load_memory()

    if not memory:
        return {"error": "memory not found"}

    q = question.lower()

    # =========================
    # 🧠 WHO IS BRAIN?
    # =========================
    if "brain" in q or "director" in q:

        return {
            "answer": "Main brain candidates",
            "files": find_by_role(memory, "decision_orchestrator")
        }

    # =========================
    # ⚙ EXECUTION CORE
    # =========================
    if "execution" in q or "engine" in q:

        return {
            "answer": "Execution core modules",
            "files": find_by_role(memory, "execution_core")
        }

    # =========================
    # 🧭 CONTROL LAYER
    # =========================
    if "control" in q:

        return {
            "answer": "Control layer modules",
            "files": find_by_role(memory, "control_layer")
        }

    # =========================
    # 🔍 SEARCH MODE
    # =========================
    if "module" in q or "file" in q:

        return {
            "answer": "Search result",
            "files": search_files(memory, q)
        }

    # =========================
    # 📊 SYSTEM OVERVIEW
    # =========================
    if "summary" in q or "system" in q:

        return memory.get("summary", {})

    # =========================
    # ❓ DEFAULT
    # =========================
    return {
        "answer": "I don't understand query yet",
        "hint": [
            "try: brain",
            "try: execution",
            "try: control",
            "try: system summary"
        ]
    }


# =========================
# ▶ ENTRY (TEST MODE)
# =========================
if __name__ == "__main__":

    while True:

        q = input("\n🧠 Ask Megabot > ")

        if q in ["exit", "quit"]:
            break

        result = query(q)

        print("\n📊 RESULT:\n")
        print(result)
