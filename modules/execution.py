import os

def save_to_memory(data):
    with open("memory.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")


def execution(data):
    print("EXECUTION:", data["result"])

    # 💾 лог
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")

    # 🚀 саморазвитие
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

    elif data["decision"] == "change_strategy":
        print("🧠 Меняю стратегию...")
        data["result"] = "strategy changed"

    # 🧠 ГЛАВНОЕ — ПАМЯТЬ
    data["memory"].append(data["decision"])

    data["log"].append("execution complete")

    # 💾 (дополнительно, можно оставить)
    save_to_memory(data)

    return data
