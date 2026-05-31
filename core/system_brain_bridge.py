# =========================================================
# 🧠 MEGABOT SYSTEM BRAIN BRIDGE
# 🧠 SINGLE SOURCE OF ARCHITECTURE TRUTH (FIXED)
# =========================================================

from core.module_router_v2 import ModuleRouterV2


class SystemBrainBridge:

    def __init__(self):

        # router создаём один раз
        self.router = ModuleRouterV2()

        self.roles = {}
        self.last_refresh = 0

        self.refresh()

    # =====================================================
    # 🔄 REFRESH (SAFE)
    # =====================================================

    def refresh(self):

        try:
            # НЕ пересканируем каждый раз тяжёлую часть
            self.roles = dict(self.router.roles)

        except Exception:
            self.roles = {}

    # =====================================================
    # 🧠 GET ROLE MODULES
    # =====================================================

    def get_role_modules(self, role: str):

        return self.roles.get(role, [])

    # =====================================================
    # ⚙ EXECUTION
    # =====================================================

    def get_execution_module(self):

        pool = self.get_role_modules("EXECUTION")
        return pool[0] if pool else "director"

    # =====================================================
    # 🔍 ANALYSIS
    # =====================================================

    def get_analysis_module(self):

        pool = self.get_role_modules("ANALYSIS")
        return pool[0] if pool else "analysis"

    # =====================================================
    # 🧠 DECISION
    # =====================================================

    def get_decision_module(self):

        pool = self.get_role_modules("DECISION")
        return pool[0] if pool else "central_decision"

    # =====================================================
    # 📊 DEBUG
    # =====================================================

    def debug(self):

        return {
            "roles": self.roles,
            "counts": {k: len(v) for k, v in self.roles.items()},
            "brain_node": self._find_brain_node()
        }

    # =====================================================
    # 🧠 BRAIN NODE
    # =====================================================

    def _find_brain_node(self):

        if self.roles.get("DECISION"):
            return self.roles["DECISION"][0]

        if self.roles.get("EXECUTION"):
            return self.roles["EXECUTION"][0]

        if self.roles.get("ANALYSIS"):
            return self.roles["ANALYSIS"][0]

        return "director"