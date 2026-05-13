import importlib
import os
import traceback
from collections import defaultdict

from core.system_state import system_state

try:
    from modules.system_registry import register_module
except Exception:
    register_module = None


# =========================================================
# ⚙️ LOG LEVELS
# =========================================================
LOG_LEVEL = os.getenv("ROUTER_LOG", "INFO")  # DEBUG | INFO | ERROR | SILENT

def log(msg, level="INFO"):
    if LOG_LEVEL == "SILENT":
        return
    if LOG_LEVEL == "ERROR" and level != "ERROR":
        return
    if LOG_LEVEL == "INFO" and level == "DEBUG":
        return
    print(msg)


# =========================================================
# 🧠 ROLE MAP
# =========================================================

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

    # =====================================================
    # 📦 LOAD MODULES (quiet)
    # =====================================================
    def load_modules(self):

        path = "modules"
        log("[RouterV2] Loading modules...", "INFO")

        if not os.path.exists(path):
            log("[RouterV2] modules folder not found", "ERROR")
            return

        for file in os.listdir(path):

            if not file.endswith(".py") or file.startswith("__"):
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

                log(f"[RouterV2] loaded: {name}", "INFO")

            except Exception as e:
                self.failed[name] = str(e)
                log(f"[RouterV2] error {name}: {e}", "ERROR")

    # =====================================================
    # 🧠 ROLE DETECTION
    # =====================================================
    def detect_role(self, name: str):
        lower = name.lower()

        for role, keys in ROLE_MAP.items():
            for k in keys:
                if k in lower:
                    return role

        return "UNKNOWN"

    def build_architecture_map(self):

        for name in self.modules:
            role = self.detect_role(name)
            self.roles[role].append(name)

        log(f"[RouterV2] roles built: {len(self.roles)}", "INFO")

    # =====================================================
    # 🔁 FLOW
    # =====================================================
    def get_flow(self):
        return [
            "CONTROL",
            "ENTRYPOINT",
            "ANALYSIS",
            "DECISION",
            "EXECUTION",
            "MEMORY"
        ]

    # =====================================================
    # 🎯 ROUTE (CLEAN OUTPUT)
    # =====================================================
    def route(self, command):

        command = self.normalize(command)

        module_name = command.get("module", "director")
        data = command.get("data", {})

        # =====================
        # STATE
        # =====================
        try:
            state = system_state.load()
            system_state.inject(data)
            state = system_state.get()
            data["system_state"] = state
        except:
            state = {}

        # =====================
        # FALLBACK
        # =====================
        if module_name not in self.modules:
            log(f"[RouterV2] fallback -> director", "ERROR")
            module_name = "director"

        module = self.modules[module_name]

        # =====================
        # EXECUTION
        # =====================
        try:
            result = module.run({
                **data,
                "system_state": state,
                "roles": dict(self.roles),
                "flow": self.get_flow()
            })

            # only summary log (IMPORTANT FIX)
            log(f"[RouterV2] ✔ {module_name} done", "INFO")

            return {
                "status": "success",
                "module": module_name,
                "result": result
            }

        except Exception as e:
            log(f"[RouterV2] crash in {module_name}: {e}", "ERROR")

            return {
                "status": "error",
                "module": module_name,
                "message": str(e),
                "trace": traceback.format_exc()
            }

    # =====================================================
    # 🧼 NORMALIZE (UNCHANGED)
    # =====================================================
    def normalize(self, command):

        if isinstance(command, dict) and "task" in command:
            return {"module": "director", "data": command}

        if isinstance(command, str):
            return {"module": "director", "data": {"task": command}}

        if not isinstance(command, dict):
            return {"module": "director", "data": {"task": str(command)}}

        if "module" not in command:
            return {"module": "director", "data": command}

        if "data" not in command:
            command["data"] = {}

        return command
