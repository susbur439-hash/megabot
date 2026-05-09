# =========================================================
# 🧠 MEGABOT CONNECTION MANAGER LAYER v1
# 🔧 SAFE LINK CONTROL (CODE vs ARCHITECTURE)
# =========================================================

import json
import os

ARCH_FILE = "architecture.json"

# =========================================================
# 🔐 RULES
# =========================================================

ALLOWED_CHANGES = {
    "imports": True,
    "module_files": True,
    "dependencies": True,

    "core_flow": False,
    "director_flow": False,
    "control_layer": False,
    "loop_structure": False
}

# =========================================================
# 📖 LOAD ARCH
# =========================================================

def load_arch():
    if not os.path.exists(ARCH_FILE):
        return None
    try:
        with open(ARCH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

# =========================================================
# 🧠 CLASSIFY LINK TYPE
# =========================================================

def classify_link(from_node, to_node):

    # архитектурные связи
    core_nodes = [
        "task_interpreter",
        "analysis",
        "planning",
        "decision",
        "execution",
        "director",
        "control_layer"
    ]

    if from_node in core_nodes or to_node in core_nodes:
        return "core_flow"

    return "code_link"

# =========================================================
# 🧠 CAN MODIFY LINK
# =========================================================

def can_modify_link(link_type):

    return ALLOWED_CHANGES.get(link_type, False)

# =========================================================
# 🔧 VALIDATE CHANGE REQUEST
# =========================================================

def validate_change(from_node, to_node):

    link_type = classify_link(from_node, to_node)

    allowed = can_modify_link(link_type)

    return {
        "from": from_node,
        "to": to_node,
        "type": link_type,
        "allowed": allowed
    }

# =========================================================
# 🧠 APPLY SAFE UPDATE (OPTIONAL HOOK)
# =========================================================

def apply_link_change(arch, from_node, to_node):

    check = validate_change(from_node, to_node)

    if not check["allowed"]:
        return {
            "status": "BLOCKED",
            "reason": "architecture-protected-link",
            "link": check
        }

    if "connections" not in arch:
        arch["connections"] = []

    arch["connections"].append({
        "from": from_node,
        "to": to_node,
        "type": check["type"]
    })

    return {
        "status": "APPLIED",
        "link": check
    }

# =========================================================
# 🧠 SUMMARY
# =========================================================

def summary():
    return {
        "allowed_changes": ALLOWED_CHANGES,
        "mode": "SAFE_SEPARATION_LAYER"
    }
