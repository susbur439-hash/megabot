# control_layer.py
# 🔒 Центральный контроль Megabot
# Блокирует хаотичное создание модулей и управляет режимами системы

class ControlLayer:

    CORE_MODULES = [
        "task_interpreter",
        "evaluation",
        "learning",
        "control_layer"
    ]

    def __init__(self):
        self.mode = "safe"
        self.block_create_module = False
        self.missing_core = []

    # =========================
    # 🔍 Проверка системы
    # =========================
    def check_system_health(self, existing_modules: list):

        self.missing_core = [
            m for m in self.CORE_MODULES
            if m not in existing_modules
        ]

        if len(self.missing_core) > 0:
            self.mode = "repair"
            self.block_create_module = True
        else:
            self.mode = "normal"
            self.block_create_module = False

        return {
            "mode": self.mode,
            "missing_core": self.missing_core,
            "block_create_module": self.block_create_module
        }

    # =========================
    # 🧠 Контроль решения
    # =========================
    def filter_decision(self, decision: str):

        # 🚨 Жесткая блокировка генерации модулей
        if self.block_create_module and decision == "create_module":
            return {
                "allowed": False,
                "forced_decision": "repair_core",
                "reason": "Core modules missing: " + ", ".join(self.missing_core)
            }

        return {
            "allowed": True,
            "decision": decision
        }

    # =========================
    # 🔧 Принудительное действие
    # =========================
    def enforce(self):

        if self.block_create_module:
            return {
                "action": "REPAIR_MODE",
                "priority": "critical",
                "target": self.missing_core
            }

        return {
            "action": "RUN_NORMAL"
        }
