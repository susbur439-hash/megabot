# core/module_router.py

import importlib
import os
import traceback

from core.system_state import system_state

# =========================================================
# 🧠 SYSTEM REGISTRY
# =========================================================

try:
    from modules.system_registry import register_module
except Exception:
    register_module = None


class ModuleRouter:

    def __init__(self):

        self.modules = {}
        self.failed_modules = {}

        self.load_modules()

    # =====================================================
    # 🔌 LOAD MODULES
    # =====================================================

    def load_modules(self):

        modules_path = "modules"

        print("[Router] Loading modules...")

        if not os.path.exists(modules_path):
            print("[Router] ERROR: modules folder not found")
            return

        for file in os.listdir(modules_path):

            if not file.endswith(".py"):
                continue

            if file.startswith("__"):
                continue

            module_name = file[:-3]

            try:

                module_path = f"modules.{module_name}"

                module = importlib.import_module(module_path)
                importlib.reload(module)

                # =========================
                # 🛡 CONTRACT CHECK
                # =========================
                if not hasattr(module, "run") or not callable(module.run):

                    self.failed_modules[module_name] = "INVALID_RUN_CONTRACT"

                    print(f"[Router] ⚠ skipped: {module_name}")
                    continue

                self.modules[module_name] = module

                # =========================
                # 🧠 REGISTRY SYNC
                # =========================
                if register_module:
                    try:
                        register_module(module_name, module)
                    except Exception as e:
                        print(f"[Registry] register failed: {e}")

                print(f"[Router] ✅ loaded: {module_name}")

            except Exception as e:

                self.failed_modules[module_name] = str(e)

                print(f"[Router] ❌ error {module_name}: {e}")
                traceback.print_exc()

        print(f"[Router] Total modules loaded: {len(self.modules)}")
        print(f"[Router] Failed modules: {len(self.failed_modules)}")

    # =====================================================
    # 📋 LIST MODULES
    # =====================================================

    def list_modules(self):
        return list(self.modules.keys())

    # =====================================================
    # 🔄 RELOAD
    # =====================================================

    def reload_modules(self):

        self.modules = {}
        self.failed_modules = {}

        self.load_modules()

        return {
            "status": "reloaded",
            "modules": self.list_modules(),
            "failed": self.failed_modules
        }

    # =====================================================
    # 🧠 NORMALIZER (STATE-AWARE)
    # =====================================================

    def normalize(self, command):

        """
        Поддержка:
        - нового state режима
        - старого dict режима
        - string режима
        """

        # =========================
        # 🧠 STATE MODE
        # =========================
        if isinstance(command, dict) and "task" in command:

            return {
                "module": "director",
                "data": command
            }

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
        # ❌ INVALID INPUT
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
    # 🎯 ROUTE (STATE CORE READY)
    # =====================================================

    def route(self, command):

        # =========================
        # 🧠 NORMALIZE
        # =========================
        command = self.normalize(command)

        module_name = command.get("module")
        data = command.get("data", {})

        # =========================
        # 🧠 LOAD SYSTEM STATE
        # =========================
        try:

            state = system_state.load()

            # inject current task/data
            system_state.inject(data)

            state = system_state.get()

            data["system_state"] = state

        except Exception as e:

            print(f"[Router] state inject error: {e}")

        # =========================
        # ❌ UNKNOWN MODULE
        # =========================
        if module_name not in self.modules:

            print(f"[Router] ❌ unknown module: {module_name}")

            return {
                "status": "error",
                "message": f"Module not found: {module_name}",
                "fallback": "director"
            }

        # =========================
        # 🚀 EXECUTION
        # =========================
        try:

            module = self.modules[module_name]

            print(f"[Router] EXECUTE -> {module_name}")

            result = module.run(data)

            # =========================
            # 🧠 UPDATE STATE
            # =========================
            try:

                state = system_state.get()

                state["last_module"] = module_name
                state["last_result"] = result

                system_state.update("last_module", module_name)
                system_state.update("last_result", result)

            except Exception as e:
                print(f"[Router] state update error: {e}")

            return {
                "status": "success",
                "module": module_name,
                "result": result
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e),
                "trace": traceback.format_exc()
            }

    # =====================================================
    # ❌ ERROR HELPER
    # =====================================================

    def _error(self, message):

        return {
            "status": "error",
            "message": message
        }
