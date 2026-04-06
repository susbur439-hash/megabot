import os
import importlib.util  # 🔥 ДОБАВИЛИ


def save_to_memory(data):
    with open("memory.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")


# 🔥 ДОБАВИЛИ ФУНКЦИЮ ЗАПУСКА
def run_python_module(module_path, data):
    try:
        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "new_module"):
            return module.new_module(data)
        elif hasattr(module, "alt_module"):
            return module.alt_module(data)
        else:
            print("⚠️ Нет функции для запуска")
            return data

    except Exception as e:
        print("❌ Ошибка при запуске модуля:", e)
        return data


def execution(data):
    print("EXECUTION:", data["result"])

    # 💾 лог
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")

    # 📁 гарантируем, что папка есть
    os.makedirs("modules", exist_ok=True)

    module_used = None  # 🔥 НОВОЕ (для опыта)

    # 🚀 1. СОЗДАНИЕ МОДУЛЯ
    if data["decision"] == "add_module":
        module_path = os.path.join("modules", "new_module.py")
        module_used = "new_module"

        if not os.path.exists(module_path):
            with open(module_path, "w", encoding="utf-8") as f:
                f.write("""def new_module(data):
    data["log"].append("new module works")
    return data
""")
            print("🔥 Создан новый модуль")
            data["result"] = "module created"
        else:
            print("ℹ️ Модуль уже существует")
            data["result"] = "module already exists"

    # 🛠 2. УЛУЧШЕНИЕ
    elif data["decision"] == "improve_module":
        module_path = os.path.join("modules", "new_module.py")
        module_used = "new_module"

        if os.path.exists(module_path):
            with open(module_path, "a", encoding="utf-8") as f:
                f.write("\n# improvement added\n")
            print("🛠 Улучшил модуль")
            data["result"] = "module improved"
        else:
            print("⚠️ Нет модуля для улучшения")
            data["result"] = "no module to improve"

    # 🔄 3. АЛЬТЕРНАТИВА
    elif data["decision"] == "create_alternative":
        module_path = os.path.join("modules", "alt_module.py")
        module_used = "alt_module"

        if not os.path.exists(module_path):
            with open(module_path, "w", encoding="utf-8") as f:
                f.write("""def alt_module(data):
    data["log"].append("alternative module works")
    return data
""")
            print("🔄 Создан альтернативный модуль")
            data["result"] = "alternative created"
        else:
            print("ℹ️ Альтернативный модуль уже существует")
            data["result"] = "alternative exists"

    # 🔥 4. ЗАПУСК МОДУЛЯ
    elif data["decision"] == "run_module":
        module_path = os.path.join("modules", "new_module.py")
        module_used = "new_module"

        if os.path.exists(module_path):
            print("🚀 Запускаю модуль...")
            data = run_python_module(module_path, data)
            data["result"] = "module executed"
        else:
            print("⚠️ Нет модуля для запуска")
            data["result"] = "no module to run"

    else:
        print("❌ Нет действия")
        data["result"] = "no action"

    # 🧠 ПАМЯТЬ
    data["memory"].append(data["decision"])

    # 🔥🔥🔥 НОВОЕ — ОПЫТ (САМОЕ ВАЖНОЕ)
    if "experience" not in data:
        data["experience"] = []

    evaluation = data.get("evaluation", {})
    score = evaluation.get("score", 50)

    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score
        })

    data["log"].append("execution complete")

    # 💾 файл памяти
    save_to_memory(data)

    return data
