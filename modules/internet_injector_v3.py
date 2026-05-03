import json
import os

MEM_FILE = "internet_memory_v2.json"

def load_memory():
    if not os.path.exists(MEM_FILE):
        return []
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def build_weights(memory):
    weights = {}

    for item in memory:
        for p, w in item.get("patterns", []):
            weights[p] = weights.get(p, 0) + w

    return weights

def inject_decision(data):
    data.setdefault("log", [])

    memory = load_memory()
    weights = build_weights(memory)

    data["internet_weights"] = weights

    score = data.get("evaluation", {}).get("score", 50)

    best_module = None
    best_score = 0

    for e in data.get("experience", []):
        if isinstance(e, dict):
            m = e.get("module")
            s = e.get("score", 0)

            if s > best_score:
                best_score = s
                best_module = m

    decision_system_power = weights.get("decision_system", 0)

    if decision_system_power > 50 and best_module:
        action = "run_module"
        module = best_module
    elif score >= 60 and best_module:
        action = "run_module"
        module = best_module
    else:
        action = "create_module"
        module = None

    if action == "run_module" and not module:
        action = "create_module"
        module = None

    data["decision"] = action
    data["module"] = module

    data["log"].append(
        f"🧠 INJECTED DECISION | action={action} | module={module}"
    )

    return data
