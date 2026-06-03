from modules.control_bus import inject, emit

def decide(data):
return decision(data)

def decision(data):

if not isinstance(data, dict):
    data = {}

data.setdefault("log", [])
data.setdefault("experience", [])
data.setdefault("evaluation", {})

data = inject(data)

experience = data.get("experience", [])
score = data.get("evaluation", {}).get("score", 50)

module_map = {}

for e in experience:

    if not isinstance(e, dict):
        continue

    module = e.get("module")
    module_score = e.get("score")

    if not module:
        continue

    if not isinstance(module_score, (int, float)):
        continue

    module_map.setdefault(module, []).append(module_score)

best_module = None
best_score = -1

for module, scores in module_map.items():

    avg = sum(scores) / len(scores)

    if avg > best_score:
        best_score = avg
        best_module = module

action = None
selected_module = None

# ====================================
# MANUAL MODULE
# ====================================

requested_module = data.get("module")

if requested_module:

    action = "run_module"
    selected_module = requested_module

# ====================================
# BEST KNOWN MODULE
# ====================================

elif best_module:

    action = "run_module"
    selected_module = best_module

# ====================================
# NO MODULES YET
# ====================================

else:

    action = "create_module"

data["decision"] = action
data["module"] = selected_module

emit({
    "phase": "decision",
    "action": action,
    "module": selected_module,
    "score": score
})

data["log"].append(
    f"decision={action} module={selected_module} best_score={best_score}"
)

return data