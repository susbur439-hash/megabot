import sys
import os

# добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ ПРАВИЛЬНЫЙ ИМПОРТ
from modules.director import run


if __name__ == "__main__":
    task = "развивай себя"

    if len(sys.argv) > 1:
        task = sys.argv[1]

    print("🚀 Megabot Director запущен")
    print("🎯 Задача:", task)

    # запуск директора
    run(task)
