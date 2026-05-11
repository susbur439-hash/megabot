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
                # CONTRACT CHECK (OS MODE)
                # =========================
                if not hasattr(module, "run") or not callable(module.run):

                    self.failed_modules[module_name] = "INVALID_RUN_CONTRACT"

                    print(f"[Router] ⚠ skipped: {module_name}")
                    continue

                self.modules[module_name] = module

                # registry sync
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
    # 📋 LIST
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
    # 🧠 OS MODE NORMALIZER (КЛЮЧЕВОЕ ДОБАВЛЕНИЕ)
    # =====================================================

    def normalize(self, command):

        """
        Приводит ВСЕ команды к единому формату
        OS MODE: Brain не имеет права ломать контракт
        """

        if isinstance(command, str):

            return {
                "module": "director",
                "data": {"task": command}
            }

        if not isinstance(command, dict):

            return {
                "module": "director",
                "data": {"task": str(command)}
            }

        # защита от brain мусора
        if "module" not in command:

            return {
                "module": "director",
                "data": command
            }

        if "data" not in command:

            command["data"] = {}

        return command

    # =====================================================
    # 🎯 ROUTE (OS MODE CORE)
    # =====================================================

    def route(self, command):

        # 🔒 normalize FIRST
        command = self.normalize(command)

        module_name = command.get("module")
        data = command.get("data", {})

        if module_name not in self.modules:

            print(f"[Router] ❌ unknown module: {module_name}")

            return {
                "status": "error",
                "message": f"Module not found: {module_name}",
                "fallback": "director"
            }

        try:

            module = self.modules[module_name]

            print(f"[Router] EXECUTE -> {module_name}")

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
