import importlib
import os
import json
import traceback
from collections import defaultdict

from core.system_state import system_state

# =========================
# ⚙️ LOG CONTROL
# =========================
LOG_LEVEL = "INFO"
# OPTIONS: "SILENT", "ERROR", "INFO"

def log(msg, level="INFO"):
    if LOG_LEVEL == "SILENT":
        return
    if LOG_LEVEL == "ERROR" and level != "ERROR":
        return
    print(msg)


# =========================
# 🧠 REGISTRY
# =========================

try:
    from modules.system_registry import register_module
except Exception:
    register_module = None


# =========================
# 🧠 ROLE MAP
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
    # 📦 LOAD
    # =========================
    def load_modules(self):

        path = "modules"
        log("[RouterV2] loading modules...", "INFO")

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
                    try:
                        register_module(name, module)
                    except Exception:
                        pass

                log(f"[RouterV2] loaded: {name}")

            except Exception as e:
                self.failed[name] = str(e)
                log(f"[RouterV2] error: {name}", "ERROR")

    # =========================
    # 🧠 ROLE DETECT
    # =========================
    def detect_role(self, name: str):
        lower = name.lower()

        for role, keys in ROLE_MAP.items():
            for k in keys:
                if k in lower:
                    return role

        return "UNKNOWN"

    # =========================
    # 🧠 ARCH MAP
    # =========================
    def build_architecture_map(self):

        self.roles = defaultdict(list)

        for name in self.modules:
            self.roles[self.detect_role(name)].append(name)

        try:
            with open("architecture_map.json", "w", encoding="utf-8") as f:
                json.dump(dict(self.roles), f, indent=2, ensure_ascii=False)
        except:
            pass

        log("[RouterV2] architecture map built")

    # =========================
    # 🔁 FLOW
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
    # 🧼 NORMALIZE
    # =========================
    def normalize(self, command):

        if isinstance(command, str):
            return {"module": "director", "data": {"task": command}}

        if not isinstance(command, dict):
            return {"module": "director", "data": {"task": str(command)}}

        if "module" not in command:
            return {"module": "director", "data": command}

        command.setdefault("data", {})
        return command

    # =========================
    # 🎯 ROUTE
    # =========================
    def route(self, command):

        command = self.normalize(command)

        try:
            system_state.load()
            system_state.inject(command)
            state = system_state.get()
        except Exception:
            state = {}

        module_name = command.get("module", "director")
        data = command.get("data", {})

        if module_name not in self.modules:
            log("[RouterV2] fallback -> director", "ERROR")
            module_name = "director"

        module = self.modules[module_name]

        try:
            result = module.run({
                **data,
                "system_state": state,
                "roles": dict(self.roles),
                "flow": self.get_flow(),
                "router_version": "v2.1"
            })

            try:
                system_state.update("last_module", module_name)
                system_state.update("last_result", result)
            except:
                pass

            return {
                "status": "success",
                "module": module_name,
                "result": result,
                "architecture_view": dict(self.roles)
            }

        except Exception as e:
            return {
                "status": "error",
                "module": module_name,
                "message": str(e),
                "trace": traceback.format_exc()
            }
