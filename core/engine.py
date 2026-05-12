from core.module_router import ModuleRouter
from core.system_state import system_state


class Engine:

    def __init__(self):
        self.router = ModuleRouter()

    def execute(self, command):
        """
        Главная точка входа системы
        """

        print("[Engine] Received command:", command)

        # =========================
        # 🧠 SYSTEM STATE CORE INTEGRATION
        # =========================
        state = system_state.inject(command)

        # загружаем внешнее состояние (memory, brain_map и т.д.)
        state = system_state.load()

        # сохраняем текущую команду в state
        state["task"] = command

        # =========================
        # 🚀 ROUTING (через единое состояние)
        # =========================
        result = self.router.route(state)

        print("[Engine] Result:", result)

        return result


# =========================
# 🔥 ТЕСТ ЗАПУСКА
# =========================
if __name__ == "__main__":

    engine = Engine()

    test_command = {
        "module": "system",
        "action": "list"
    }

    engine.execute(test_command)
