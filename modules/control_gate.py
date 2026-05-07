# =========================
# 🧠 MEGABOT CONTROL GATE v1
# =========================
# 🔒 Разделяет runtime и builder
# 🔒 Блокирует опасные действия в runtime
# =========================

import os


class ControlGate:

    def __init__(self):
        self.mode = "runtime"   # runtime | builder | safe

    # =========================
    # 🔍 DETECT CONTEXT
    # =========================
    def detect_context(self, data: dict):

        task = data.get("task", "")

        # 🧠 builder запускается ТОЛЬКО вручную / CI
        if "controlled_builder" in task or "builder" in task:
            self.mode = "builder"
        else:
            self.mode = "runtime"

        return self.mode

    # =========================
    # 🚫 BLOCK DANGEROUS ACTIONS
    # =========================
    def filter_decision(self, data: dict):

        decision = data.get("decision")

        # =========================
        # 🔴 RUNTIME LOCK
        # =========================
        if self.mode == "runtime":

            # ❌ builder НЕ может запускаться из runtime
            if "builder" in str(data.get("task", "")):
                return {
                    "allowed": False,
                    "forced_decision": "run_module",
                    "reason": "Builder execution blocked in runtime"
                }

            # ❌ защита от бесконечного создания модулей
            if decision == "create_module":
                create_repeats = data.get("create_repeats", 0)

                if create_repeats >= 2:
                    return {
                        "allowed": False,
                        "forced_decision": "run_module",
                        "reason": "Create loop detected"
                    }

        # =========================
        # 🟡 BUILDER MODE
        # =========================
        if self.mode == "builder":

            # builder может только анализировать систему
            allowed = decision in ["analyze", "audit", "fix", "add", "delete"]

            if not allowed:
                return {
                    "allowed": False,
                    "forced_decision": "audit",
                    "reason": "Invalid builder action"
                }

        return {
            "allowed": True,
            "decision": decision
        }

    # =========================
    # 🔧 FORCE MODE
    # =========================
    def enforce(self, data: dict):

        if self.mode == "runtime":
            return {
                "mode": "runtime",
                "status": "normal"
            }

        if self.mode == "builder":
            return {
                "mode": "builder",
                "status": "active"
            }


# =========================
# 🌐 SINGLETON
# =========================
CONTROL_GATE = ControlGate()


# =========================
# 🚀 API
# =========================
def detect(data):
    return CONTROL_GATE.detect_context(data)


def filter_decision(data):
    return CONTROL_GATE.filter_decision(data)


def enforce(data):
    return CONTROL_GATE.enforce(data)
