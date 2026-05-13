import importlib
import os
import json
import traceback
from collections import defaultdict

from core.system_state import system_state

try:
    from modules.system_registry import register_module
except Exception:
    register_module = None


# =========================================================
# ⚙️ LOG LEVEL CONTROL
# =========================================================
# silent  -> почти ничего
# normal  -> краткие логи
# debug   -> всё как сейчас (но контролируемо)
# =========================================================

LOG_LEVEL = "normal"


def log(msg, level="normal"):
    if LOG_LEVEL == "silent":
        return
    if LOG_LEVEL == "normal" and level == "debug":
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
    # 📦 LOAD MODULES (SAFE)
    # =====================================================

    def load_modules(self):

        path = "modules"

        log("[RouterV2] loading modules...")

        if not os.path.exists(path):
            log("[RouterV2] ERROR: modules folder not found")
            return

        ok_count = 0

        for file in os.listdir(path):

            if not file.endswith(".py"):
                continue
            if file.startswith("__"):
                continue

            name = file[:-3]

            try:
                module = importlib.import_module(f"modules.{name}")
                importlib.reload(module)

                if not hasattr(module, "run") or not callable(module.run):
                    self.failed[name] = "NO_RUN"
                    continue

                self.modules[name] = module
                ok_count += 1

                if register_module:
                    try:
                        register_module(name, module)
                    except Exception:
                        pass

            except Exception as e:
                self.failed[name] = str(e)

        log(f"[RouterV2] modules OK={ok_count} FAILED={len(self.failed)}")

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

    # =====================================================
    # 🧠 ARCHITECTURE MAP
    # =====================================================

    def build_architecture_map(self):

        self.roles = defaultdict(list)

        for name in self.modules.keys():
            role = self.detect_role(name)
            self.roles[role].append(name)

        try:
            with open("architecture_map.json", "w", encoding="utf-8") as f:
                json.dump(dict(self.roles), f, indent=2, ensure_ascii=False)

        except Exception:
            pass

        log("[RouterV2] architecture map ready")

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
    # 🧼 NORMALIZER
    # =====================================================

    def normalize(self, command):

        if isinstance(command, str):
            return {"module": "director", "data": {"task": command}}

        if not isinstance(command, dict):
            return {"module": "director", "data": {"task": str(command)}}

        if "module" not in command:
            return {"module": "director", "data": command}

        if "data" not in command:
            command["data"] = {}

        return command

    # =====================================================
    # 🎯 ROUTE (CLEAN + SAFE)
    # =====================================================

    def route(self, command):

        command = self.normalize(command)

        # ---- STATE (SAFE LOAD) ----
        try:
            system_state.inject(command)
            state = system_state.get()
        except Exception:
            state = {}

        module_name = command.get("module", "director")
        data = command.get("data", {})

        if module_name not in self.modules:
            log(f"[RouterV2] fallback -> director")
            module_name = "director"

        module = self.modules.get(module_name)

        if not module:
            return {
                "status": "error",
                "message": "No module available"
            }

        log(f"[RouterV2] EXEC -> {module_name}")

        try:
            result = module.run({
                **data,
                "system_state": state,
                "roles": dict(self.roles),
                "flow": self.get_flow(),
                "router_version": "v2.1-clean"
            })

            try:
                system_state.update("last_module", module_name)
                system_state.update("last_result", result)
            except Exception:
                pass

            return {
                "status": "success",
                "module": module_name,
                "result": result,
                "roles_summary": {
                    k: len(v) for k, v in self.roles.items()
                },
                "flow": self.get_flow()
            }

        except Exception as e:

            return {
                "status": "error",
                "module": module_name,
                "message": str(e),
                "trace": traceback.format_exc()
            }
