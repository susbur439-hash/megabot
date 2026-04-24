import sys
import os

# добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# =========================
# 🔌 ENGINE
# =========================
try:
    from core.engine import Engine
    ENGINE_AVAILABLE = True
except Exception as e:
    print("[Engine] not available:", e)
    ENGINE_AVAILABLE = False

# =========================
# 🎯 DIRECTOR (старый слой)
# =========================
from modules.director import run as director_run


def run_direct_command(cmd):
    """
    🔥 Прямой запуск python-файлов (обход Megabot)
    """
    if cmd.endswith(".py") and os.path.exists(cmd):
        print(f"🚀 Direct run: {cmd}")
        os.system(f"python {cmd}")
        return True
    return False


if __name__ == "__main__":
    task = "развивай себя"

    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])

    print("🚀 Megabot старт")
    print("🎯 Задача:", task)

    # =========================
    # 🔥 DIRECT MODE
    # =========================
    if run_direct_command(task):
        sys.exit()

    # =========================
    # 🧠 НОВАЯ АРХИТЕКТУРА (Engine)
    # =========================
    if ENGINE_AVAILABLE:
        print("[Main] Trying Engine...")

        try:
            engine = Engine()

            command = {
                "module": "system",
                "action": "list"
            }

            result = engine.execute(command)

            print("[Main] Engine result:", result)

        except Exception as e:
            print("[Main] Engine error:", e)

    # =========================
    # 🤖 СТАРАЯ СИСТЕМА (fallback)
    # =========================
    print("[Main] Running Director fallback...")
    director_run(task)
