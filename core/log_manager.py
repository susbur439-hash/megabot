import json
import traceback

# =========================
# ⚙️ CLEAN LOG CONFIG
# =========================

LOG_MODE = "CLEAN"
# CLEAN | DEBUG | SILENT


def short(obj, max_keys=5):

    """
    Сильно обрезает большие структуры
    """

    if isinstance(obj, dict):
        return {
            k: short(v)
            for i, (k, v) in enumerate(obj.items())
            if i < max_keys
        }

    if isinstance(obj, list):
        return obj[:5]

    return obj


def log_decision(decision):

    if LOG_MODE == "SILENT":
        return

    if LOG_MODE == "DEBUG":
        print("[DECISION FULL]:")
        print(json.dumps(decision, indent=2, ensure_ascii=False))
        return

    # CLEAN MODE
    print("[DECISION]:", {
        "module": decision.get("module"),
        "keys": list(decision.keys())[:5]
    })


def log_state(state):

    if LOG_MODE != "DEBUG":
        return

    print("[STATE]:")
    try:
        print(json.dumps(short(state), indent=2, ensure_ascii=False))
    except:
        print(traceback.format_exc())
