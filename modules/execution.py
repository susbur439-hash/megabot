import os
import importlib.util


def save_to_memory(data):
    with open("memory.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")


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

    # 📁 гарантируем папку
    os.makedirs("modules", exist_ok=True)

    module_used = None

    # 🔥 ВЫБОР ЛУЧШЕГО МОДУЛЯ (НОВОЕ)
    best_module = None
    best_score = 0

    for exp in data.get("experience", []):
        if isinstance(exp, dict):
            s = exp.get("score", 0)
            m = exp.get("module")
            if s > best_score:
                best_score = s
                best_module = m

    # 🚀 1. СОЗДАНИЕ
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

    # 🛠 2. УЛУЧШЕНИЕ (УЛУЧШЕНО)
    elif data["decision"] == "improve_module":
        module_path = os.path.join("modules", "new_module.py")
        module_used = "new_module"

        if os.path.exists(module_path):
            with open(module_path, "a", encoding="utf-8") as f:
                f.write(f"\n# improvement score boost attempt\n")
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

    # 🔥 4. ЗАПУСК (УЛУЧШЕНО)
    elif data["decision"] == "run_module":

        # 🔥 если есть лучший — используем его
        if best_module == "alt_module":
            module_path = os.path.join("modules", "alt_module.py")
            module_used = "alt_module"
        else:
            module_path = os.path.join("modules", "new_module.py")
            module_used = "new_module"

        if os.path.exists(module_path):
            print(f"🚀 Запускаю модуль: {module_used}")
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

    # 🔥🔥🔥 ОПЫТ (УЛУЧШЕН)
    if "experience" not in data:
        data["experience"] = []

    evaluation = data.get("evaluation", {})
    score = evaluation.get("score", 50)

    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score
        })

        # 🔥 ОГРАНИЧЕНИЕ ПАМЯТИ (НОВОЕ)
        if len(data["experience"]) > 50:
            data["experience"] = data["experience"][-50:]

    data["log"].append(f"execution complete (used: {module_used}, best: {best_module})")

    # 💾 файл памяти
    save_to_memory(data)

    return data
