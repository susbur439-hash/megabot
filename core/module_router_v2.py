import importlib
import os
import traceback
from collections import defaultdict

from core.system_state import system_state

try:
    from modules.system_registry import register_module
except:
    register_module = None


# =========================
# 🧠 ARCHITECTURE MAP
# =========================

ROLE_MAP = {
    "ENTRYPOINT": ["main", "app", "start", "bot_start"],
    "CONTROL": ["control", "router", "panel", "gateway"],
    "DECISION": ["decision", "brain", "controller"],
    "EXECUTION": ["execution", "executor", "action", "run"],
    "ANALYSIS": ["analysis", "analyzer", "scan"],
    "MEMORY": ["memory", "snapshot", "storage"],
    "LEARNING": ["learn", "learning", "adaptive"]
}


class ModuleRouterV2:

    def __init__(self):
        self.modules = {}
        self.roles = defaultdict(list)
        self.failed = {}

        self.load_modules()
        self.build_architecture_map()

    # =========================
    # 📦 LOAD MODULES
    # =========================
    def load_modules(self):

        path = "modules"
        print("[RouterV2] Loading modules...")

        if not os.path.exists(path):
            print("[RouterV2] ERROR: modules folder not found")
            return

        for file in os.listdir(path):

            if not file.endswith(".py"):
                continue
            if file.startswith("__"):
                continue

            name = file[:-3]

            try:
                module = importlib.import_module(f"modules.{name}")
                importlib.reload(module)

                if not hasattr(module, "run"):
                    self.failed[name] = "NO_RUN"
                    continue

                self.modules[name] = module

                if register_module:
                    register_module(name, module)

                print(f"[RouterV2] loaded: {name}")

            except Exception as e:
                self.failed[name] = str(e)
                print(f"[RouterV2] error {name}: {e}")
                traceback.print_exc()

    # =========================
    # 🧠 ARCHITECTURE UNDERSTANDING
    # =========================
    def detect_role(self, name: str):

        lower = name.lower()

        for role, keys in ROLE_MAP.items():
            for k in keys:
                if k in lower:
                    return role

        return "UNKNOWN"

    def build_architecture_map(self):

        for name in self.modules.keys():
            role = self.detect_role(name)
            self.roles[role].append(name)

        print("[RouterV2] Architecture map built")

    # =========================
    # 🔁 FLOW EXECUTION MODEL
    # =========================
    def get_flow(self):

        return [
            "CONTROL",
            "ENTRYPOINT",
            "ANALYSIS",
            "DECISION",
            "EXECUTION",
            "MEMORY"
        ]

    # =========================
    # 🎯 ROUTE (SMART)
    # =========================
    def route(self, command):

        try:
            state = system_state.load()
            system_state.inject(command)
            state = system_state.get()

        except:
            state = {}

        module_name = command.get("module", "director")
        data = command.get("data", {})

        # =========================
        # 🧠 FLOW VALIDATION
        # =========================
        if module_name not in self.modules:

            print(f"[RouterV2] fallback -> director")
            module_name = "director"

        module = self.modules[module_name]

        print(f"[RouterV2] EXECUTE -> {module_name}")

        try:
            result = module.run({
                **data,
                "system_state": state,
                "roles": dict(self.roles),
                "flow": self.get_flow()
            })

            return {
                "status": "success",
                "module": module_name,
                "result": result,
                "architecture_view": dict(self.roles)
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e),
                "trace": traceback.format_exc()
            }
