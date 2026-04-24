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
    if isinstance(cmd, str) and cmd.endswith(".py") and os.path.exists(cmd):
        print(f"🚀 Direct run: {cmd}")
        os.system(f"python {cmd}")
        return True
    return False


def engine_can_handle(result):
    """
    🧠 определяем, смог ли Engine обработать задачу
    """
    if result is None:
        return False

    if isinstance(result, dict):
        # если есть явный статус ошибки или пустой результат
        if result.get("status") == "error":
            return False

        # если Engine вернул осмысленный ответ
        if result.get("status") == "ok":
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

    engine_result = None
    used_engine = False

    # =========================
    # 🧠 ENGINE TRY FIRST
    # =========================
    if ENGINE_AVAILABLE:
        print("[Main] Trying Engine...")

        try:
            engine = Engine()

            command = {
                "module": "system",
                "action": "list",
                "task": task
            }

            engine_result = engine.execute(command)
            used_engine = True

            print("[Main] Engine result:", engine_result)

        except Exception as e:
            print("[Main] Engine error:", e)

    # =========================
    # 🔁 DECISION: ENGINE vs DIRECTOR
    # =========================
    if used_engine and engine_can_handle(engine_result):
        print("[Main] Engine handled task → skipping Director")
    else:
        print("[Main] Running Director fallback...")
        director_run(task)
