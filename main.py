import sys
import os

# добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ ПРАВИЛЬНЫЙ ИМПОРТ
from modules.director import run


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

    print("🚀 Megabot Director запущен")
    print("🎯 Задача:", task)

    # =========================
    # 🔥 НОВОЕ: режим команды
    # =========================
    if run_direct_command(task):
        sys.exit()

    # =========================
    # 🤖 Обычный режим Megabot
    # =========================
    run(task)
