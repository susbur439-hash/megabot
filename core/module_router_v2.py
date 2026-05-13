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


# =========================
# 🧠 ARCHITECTURE ROLE MAP
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

    # =====================================================
    # 🚀 INIT
    # =====================================================

    def __init__(self):

        self.modules = {}
        self.roles = defaultdict(list)
        self.failed = {}

        self.load_modules()
        self.build_architecture_map()

    # =====================================================
    # 📦 LOAD MODULES
    # =====================================================

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

                module_path = f"modules.{name}"

                module = importlib.import_module(module_path)

                importlib.reload(module)

                # =========================
                # 🛡 RUN CONTRACT CHECK
                # =========================

                if not hasattr(module, "run"):

                    self.failed[name] = "NO_RUN"

                    print(f"[RouterV2] skipped: {name}")

                    continue

                self.modules[name] = module

                # =========================
                # 🧠 REGISTRY
                # =========================

                if register_module:

                    try:
                        register_module(name, module)

                    except Exception as e:
                        print(f"[RouterV2] registry error: {e}")

                print(f"[RouterV2] loaded: {name}")

            except Exception as e:

                self.failed[name] = str(e)

                print(f"[RouterV2] error {name}: {e}")

                traceback.print_exc()

        print(f"[RouterV2] modules loaded: {len(self.modules)}")
        print(f"[RouterV2] failed modules: {len(self.failed)}")

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

        # =========================
        # 💾 SAVE ARCHITECTURE
        # =========================

        try:

            with open(
                "architecture_map.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    dict(self.roles),
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            print("[RouterV2] architecture_map.json saved")

        except Exception as e:

            print(f"[RouterV2] save architecture error: {e}")

        print("[RouterV2] Architecture map built")

    # =====================================================
    # 🔁 SYSTEM FLOW
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

        # =========================
        # 📝 STRING MODE
        # =========================

        if isinstance(command, str):

            return {
                "module": "director",
                "data": {
                    "task": command
                }
            }

        # =========================
        # ❌ INVALID MODE
        # =========================

        if not isinstance(command, dict):

            return {
                "module": "director",
                "data": {
                    "task": str(command)
                }
            }

        # =========================
        # 🧠 AUTO DIRECTOR
        # =========================

        if "module" not in command:

            return {
                "module": "director",
                "data": command
            }

        # =========================
        # 📦 ENSURE DATA
        # =========================

        if "data" not in command:

            command["data"] = {}

        return command

    # =====================================================
    # 🎯 ROUTE
    # =====================================================

    def route(self, command):

        # =========================
        # 🧼 NORMALIZE INPUT
        # =========================

        command = self.normalize(command)

        # =========================
        # 🧠 LOAD SYSTEM STATE
        # =========================

        try:

            system_state.load()

            system_state.inject(command)

            state = system_state.get()

        except Exception as e:

            print(f"[RouterV2] state error: {e}")

            state = {}

        # =========================
        # 📦 COMMAND
        # =========================

        module_name = command.get("module", "director")

        data = command.get("data", {})

        # =========================
        # 🛡 MODULE VALIDATION
        # =========================

        if module_name not in self.modules:

            print(f"[RouterV2] fallback -> director")

            module_name = "director"

        module = self.modules[module_name]

        print(f"[RouterV2] EXECUTE -> {module_name}")

        # =========================
        # 🚀 EXECUTION
        # =========================

        try:

            result = module.run({

                **data,

                "system_state": state,

                "roles": dict(self.roles),

                "flow": self.get_flow(),

                "router_version": "v2.1"

            })

            # =========================
            # 🧠 UPDATE STATE
            # =========================

            try:

                system_state.update(
                    "last_module",
                    module_name
                )

                system_state.update(
                    "last_result",
                    result
                )

            except Exception as e:

                print(f"[RouterV2] state update error: {e}")

            return {

                "status": "success",

                "module": module_name,

                "result": result,

                "architecture_view": dict(self.roles),

                "flow": self.get_flow()

            }

        except Exception as e:

            return {

                "status": "error",

                "module": module_name,

                "message": str(e),

                "trace": traceback.format_exc()

            }
