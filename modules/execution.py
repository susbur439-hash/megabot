import os


def save_to_memory(data):
    with open("memory.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")


def execution(data):
    print("EXECUTION:", data["result"])

    # 💾 лог
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")

    # 📁 гарантируем, что папка есть
    os.makedirs("modules", exist_ok=True)

    # 🚀 1. СОЗДАНИЕ МОДУЛЯ
    if data["decision"] == "add_module":
        module_path = os.path.join("modules", "new_module.py")

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

    else:
        print("❌ Нет действия")
        data["result"] = "no action"

    # 🧠 ПАМЯТЬ
    data["memory"].append(data["decision"])

    data["log"].append("execution complete")

    # 💾 файл памяти
    save_to_memory(data)

    return data
