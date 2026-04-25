import importlib
import os
import traceback


class ModuleRouter:
    def __init__(self):
        self.modules = {}
        self.load_modules()

    # =========================
    # 🔌 LOAD MODULES
    # =========================
    def load_modules(self):
        modules_path = "modules"

        print("[Router] Loading modules...")

        if not os.path.exists(modules_path):
            print("[Router] ERROR: modules folder not found")
            return

        for file in os.listdir(modules_path):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]

                try:
                    module_path = f"modules.{module_name}"
                    module = importlib.import_module(module_path)

                    # reload-safe (ВАЖНО)
                    importlib.reload(module)

                    if hasattr(module, "run"):
                        self.modules[module_name] = module
                        print(f"[Router] ✅ loaded: {module_name}")
                    else:
                        print(f"[Router] ⚠ skipped: {module_name}")

                except Exception as e:
                    print(f"[Router] ❌ error {module_name}: {e}")
                    traceback.print_exc()

        print(f"[Router] Total modules loaded: {len(self.modules)}")

    # =========================
    # 📋 LIST
    # =========================
    def list_modules(self):
        return list(self.modules.keys())

    # =========================
    # 🔄 RELOAD
    # =========================
    def reload_modules(self):
        self.modules = {}
        self.load_modules()
        return {"status": "reloaded", "modules": self.list_modules()}

    # =========================
    # 🎯 EXECUTION ONLY
    # =========================
    def route(self, command):

        if not isinstance(command, dict):
            return self._error("Command must be dict")

        module_name = command.get("module")
        data = command.get("data", {})

        if not module_name:
            return self._error("No module specified")

        if module_name not in self.modules:
            return self._error(f"Module not found: {module_name}")

        try:
            module = self.modules[module_name]
            return module.run(data)

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "trace": traceback.format_exc()
            }

    # =========================
    # ❌ ERROR
    # =========================
    def _error(self, message):
        return {
            "status": "error",
            "message": message
        }
