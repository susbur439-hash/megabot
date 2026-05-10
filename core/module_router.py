import importlib
import os
import traceback

# =========================================================
# 🧠 SYSTEM REGISTRY
# =========================================================

try:
    from modules.system_registry import register_module
except:
    register_module = None


class ModuleRouter:

    def __init__(self):

        self.modules = {}

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

            # -------------------------------------------------
            # ONLY PY FILES
            # -------------------------------------------------

            if not file.endswith(".py"):
                continue

            if file.startswith("__"):
                continue

            module_name = file[:-3]

            try:

                module_path = f"modules.{module_name}"

                # -------------------------------------------------
                # IMPORT
                # -------------------------------------------------

                module = importlib.import_module(module_path)

                # reload-safe
                importlib.reload(module)

                # -------------------------------------------------
                # RUN CHECK
                # -------------------------------------------------

                if hasattr(module, "run"):

                    self.modules[module_name] = module

                    # =============================================
                    # 🧠 REGISTRY SYNC
                    # =============================================

                    if register_module:

                        try:

                            register_module(
                                module_name,
                                module
                            )

                        except Exception as e:

                            print(
                                f"[Registry] "
                                f"register failed: {e}"
                            )

                    print(
                        f"[Router] ✅ loaded: "
                        f"{module_name}"
                    )

                else:

                    print(
                        f"[Router] ⚠ skipped: "
                        f"{module_name}"
                    )

            except Exception as e:

                print(
                    f"[Router] ❌ error "
                    f"{module_name}: {e}"
                )

                traceback.print_exc()

        print(
            f"[Router] Total modules loaded: "
            f"{len(self.modules)}"
        )

    # =====================================================
    # 📋 LIST
    # =====================================================

    def list_modules(self):

        return list(self.modules.keys())

    # =====================================================
    # 🔄 RELOAD
    # =====================================================

    def reload_modules(self):

        self.modules = {}

        self.load_modules()

        return {
            "status": "reloaded",
            "modules": self.list_modules()
        }

    # =====================================================
    # 🎯 ROUTE
    # =====================================================

    def route(self, command):

        if not isinstance(command, dict):

            return self._error(
                "Command must be dict"
            )

        module_name = command.get("module")

        data = command.get("data", {})

        if not module_name:

            return self._error(
                "No module specified"
            )

        if module_name not in self.modules:

            return self._error(
                f"Module not found: {module_name}"
            )

        try:

            module = self.modules[module_name]

            print(
                f"[Router] EXECUTE -> "
                f"{module_name}"
            )

            result = module.run(data)

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
    # ❌ ERROR
    # =====================================================

    def _error(self, message):

        return {
            "status": "error",
            "message": message
        }
