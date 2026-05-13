import json
import traceback

# =========================
# ⚙️ GLOBAL MODE
# =========================

LOG_MODE = "CLEAN"
# CLEAN | DEBUG | SILENT


# =========================
# 🧠 UTIL: SHORTENER
# =========================

def short(obj, max_keys=5):

    if isinstance(obj, dict):
        return {
            k: short(v)
            for i, (k, v) in enumerate(obj.items())
            if i < max_keys
        }

    if isinstance(obj, list):
        return obj[:5]

    return obj


# =========================
# 🧠 CORE LOGGER
# =========================

class LogManager:

    def set_mode(self, mode: str):
        global LOG_MODE
        LOG_MODE = mode

    def log(self, *args):

        if LOG_MODE == "SILENT":
            return

        print(*args)

    # =====================
    # 🧠 DECISION LOG
    # =====================

    def decision(self, decision: dict):

        if LOG_MODE == "SILENT":
            return

        if LOG_MODE == "DEBUG":
            print("[DECISION FULL]:")
            print(json.dumps(decision, indent=2, ensure_ascii=False))
            return

        print("[DECISION]:", {
            "module": decision.get("module"),
            "keys": list(decision.keys())[:3]
        })

    # =====================
    # 🧠 STATE LOG
    # =====================

    def state(self, state: dict):

        if LOG_MODE != "DEBUG":
            return

        print("[STATE]:")
        try:
            print(json.dumps(short(state), indent=2, ensure_ascii=False))
        except:
            print(traceback.format_exc())


# =========================
# 🚀 SINGLETON
# =========================

log_manager = LogManager()
