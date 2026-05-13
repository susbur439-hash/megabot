import json
import traceback

# =========================
# ⚙️ LOG MODES
# =========================

CLEAN = "CLEAN"
DEBUG = "DEBUG"
SILENT = "SILENT"


class LogManager:

    def __init__(self):
        self.mode = CLEAN

    # =========================
    # ⚙️ MODE CONTROL
    # =========================

    def set_mode(self, mode: str):
        self.mode = mode

    # =========================
    # 🧠 SHORTENER (SAFE)
    # =========================

    def short(self, obj, depth=2, max_items=5):

        if depth <= 0:
            return "..."

        if isinstance(obj, dict):
            return {
                k: self.short(v, depth - 1, max_items)
                for i, (k, v) in enumerate(obj.items())
                if i < max_items
            }

        if isinstance(obj, list):
            return obj[:max_items]

        return obj

    # =========================
    # 🧠 BASE LOG
    # =========================

    def log(self, *args):

        if self.mode == SILENT:
            return

        print(*args)

    # =========================
    # 🧠 DECISION LOG
    # =========================

    def decision(self, decision: dict):

        if self.mode == SILENT:
            return

        if self.mode == DEBUG:
            print("[DECISION FULL]")
            print(json.dumps(decision, indent=2, ensure_ascii=False))
            return

        print("[DECISION]", {
            "module": decision.get("module"),
            "keys": list(decision.keys())[:3]
        })

    # =========================
    # 🧠 STATE LOG (SAFE)
    # =========================

    def state(self, state: dict):

        if self.mode != DEBUG:
            return

        print("[STATE]")
        try:
            print(json.dumps(self.short(state), indent=2, ensure_ascii=False))
        except:
            print(traceback.format_exc())

    # =========================
    # 🧠 SYSTEM STATE SUMMARY
    # =========================

    def system_state(self, state: dict):

        if self.mode == SILENT:
            return

        summary = {
            "cycle": state.get("cycle"),
            "mode": state.get("mode"),
            "progress": state.get("goal", {}).get("progress"),
            "module": state.get("last_module")
        }

        print("[STATE SUMMARY]", summary)


# =========================
# 🚀 SINGLETON
# =========================

log_manager = LogManager()
