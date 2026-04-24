# core/module_router.py

import importlib
import os
import traceback


class ModuleRouter:
    def __init__(self):
        self.modules = {}
        self.module_info = {}
        self.load_modules()

    # =========================
    # 🔌 ЗАГРУЗКА МОДУЛЕЙ
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
                    module = importlib.import_module(f"modules.{module_name}")

                    if hasattr(module, "run"):
                        self.modules[module_name] = module

                        self.module_info[module_name] = {
                            "has_run": True,
                            "file": file
                        }

                        print(f"[Router] ✅ loaded: {module_name}")
                    else:
                        print(f"[Router] ⚠ skipped (no run): {module_name}")

                except Exception as e:
                    print(f"[Router] ❌ error loading {module_name}: {e}")
                    traceback.print_exc()

        print(f"[Router] Total modules loaded: {len(self.modules)}")

    # =========================
    # 📋 СПИСОК МОДУЛЕЙ
    # =========================
    def list_modules(self):
        return list(self.modules.keys())

    # =========================
    # 🔄 ПЕРЕЗАГРУЗКА
    # =========================
    def reload_modules(self):
        self.modules = {}
        self.module_info = {}
        self.load_modules()
        return {"status": "reloaded", "modules": self.list_modules()}

    # =========================
    # 🎯 ВЫПОЛНЕНИЕ КОМАНДЫ
    # =========================
    def route(self, command):
        """
        command = {
            "module": "module_name",
            "action": "optional",
            "data": {}
        }
        """

        if not isinstance(command, dict):
            return self._error("Command must be a dict")

        module_name = command.get("module")
        data = command.get("data", {})
        action = command.get("action", None)

        if not module_name:
            return self._error("No module specified")

        # системные команды
        if module_name == "system":
            return self._handle_system(action)

        if module_name not in self.modules:
            return self._error(f"Module '{module_name}' not found")

        module = self.modules[module_name]

        try:
            # если модуль поддерживает action
            if hasattr(module, "run"):
                result = module.run(data)

            else:
                return self._error(f"Module '{module_name}' has no run()")

            return {
                "status": "ok",
                "module": module_name,
                "action": action,
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "module": module_name,
                "message": str(e),
                "trace": traceback.format_exc()
            }

    # =========================
    # ⚙️ SYSTEM COMMANDS
    # =========================
    def _handle_system(self, action):
        if action == "list":
            return {
                "status": "ok",
                "modules": self.list_modules()
            }

        elif action == "reload":
            return self.reload_modules()

        else:
            return self._error(f"Unknown system action '{action}'")

    # =========================
    # ❌ ОШИБКА
    # =========================
    def _error(self, message):
        return {
            "status": "error",
            "message": message
        }
