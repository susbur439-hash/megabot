# core/engine.py

from core.module_router import ModuleRouter


class Engine:
    def __init__(self):
        self.router = ModuleRouter()

    def execute(self, command):
        """
        Главная точка входа системы
        """
        print("[Engine] Received command:", command)

        result = self.router.route(command)

        print("[Engine] Result:", result)

        return result


# =========================
# 🔥 ТЕСТ ЗАПУСКА
# =========================
if __name__ == "__main__":
    engine = Engine()

    # тестовая команда
    test_command = {
        "module": "system",
        "action": "list"
    }

    engine.execute(test_command)
