# =========================================================
# 🧠 MEGABOT SYSTEM BRAIN BRIDGE
# 🧠 SINGLE SOURCE OF ARCHITECTURE TRUTH
# =========================================================

from core.module_router_v2 import ModuleRouterV2


class SystemBrainBridge:

    def __init__(self):

        # загружаем реальный роутер
        self.router = ModuleRouterV2()

        # архитектурное состояние
        self.roles = {}
        self.refresh()

    # =====================================================
    # 🔄 REFRESH ARCHITECTURE
    # =====================================================

    def refresh(self):

        self.router.build_architecture_map()
        self.roles = self.router.roles

    # =====================================================
    # 🧠 GET ROLE MODULES
    # =====================================================

    def get_role_modules(self, role: str):

        return self.roles.get(role, [])

    # =====================================================
    # ⚙ EXECUTION LAYER
    # =====================================================

    def get_execution_module(self):

        pool = self.get_role_modules("EXECUTION")
        return pool[0] if pool else "director"

    # =====================================================
    # 🔍 ANALYSIS LAYER
    # =====================================================

    def get_analysis_module(self):

        pool = self.get_role_modules("ANALYSIS")
        return pool[0] if pool else "analysis"

    # =====================================================
    # 🧠 DECISION LAYER
    # =====================================================

    def get_decision_module(self):

        pool = self.get_role_modules("DECISION")
        return pool[0] if pool else "central_decision"

    # =====================================================
    # 📊 DEBUG INFO
    # =====================================================

    def debug(self):

        return {
            "roles": dict(self.roles),
            "counts": {k: len(v) for k, v in self.roles.items()},
            "brain_node": self._find_brain_node()
        }

    # =====================================================
    # 🧠 SIMPLE BRAIN NODE HEURISTIC
    # =====================================================

    def _find_brain_node(self):

        if "DECISION" in self.roles:
            return self.roles["DECISION"][0]

        if "EXECUTION" in self.roles:
            return self.roles["EXECUTION"][0]

        if "ANALYSIS" in self.roles:
            return self.roles["ANALYSIS"][0]

        return "director"