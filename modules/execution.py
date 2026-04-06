import os


def save_to_memory(data):
    with open("memory.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")


def execution(data):
    print("EXECUTION:", data["result"])

    # 💾 лог
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")

    # 🚀 1. СОЗДАНИЕ МОДУЛЯ
    if data["decision"] == "add_module":
        module_name = "new_module.py"
        module_path = os.path.join("modules", module_name)

        if not os.path.exists(module_path):
            with open(module_path, "w", encoding="utf-8") as f:
                f.write("""def new_module(data):
    data["log"].append("new module works")
    return data
""")
            print("🔥 Создан новый модуль:", module_name)
        else:
            print("ℹ️ Модуль уже существует")

    # 🛠 2. УЛУЧШЕНИЕ МОДУЛЯ
    elif data["decision"] == "improve_module":
        module_path = os.path.join("modules", "new_module.py")

        if os.path.exists(module_path):
            with open(module_path, "a", encoding="utf-8") as f:
                f.write("\n# improvement added\n")
            print("🛠 Улучшил модуль")
        else:
            print("⚠️ Нет модуля для улучшения")

    # 🔄 3. АЛЬТЕРНАТИВА
    elif data["decision"] == "create_alternative":
        module_name = "alt_module.py"
        module_path = os.path.join("modules", module_name)

        if not os.path.exists(module_path):
            with open(module_path, "w", encoding="utf-8") as f:
                f.write("""def alt_module(data):
    data["log"].append("alternative module works")
    return data
""")
            print("🔄 Создан альтернативный модуль:", module_name)
        else:
            print("ℹ️ Альтернативный модуль уже существует")

    # 🧠 СТАРОЕ (оставим для логики)
    elif data["decision"] == "change_strategy":
        print("🧠 Меняю стратегию...")
        data["result"] = "strategy changed"

    else:
        print("❌ Нет действия")

    # 🧠 ПАМЯТЬ
    data["memory"].append(data["decision"])

    data["log"].append("execution complete")

    # 💾 файл памяти
    save_to_memory(data)

    return data
