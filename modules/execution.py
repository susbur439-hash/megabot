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

        if hasattr(module, "run"):
            return module.run(data)
        else:
            print("⚠️ Нет функции run()")
            return data

    except Exception as e:
        print("❌ Ошибка:", e)
        return data


# 🔥 получаем список всех модулей
def get_all_modules():
    if not os.path.exists("modules"):
        return []

    return [f for f in os.listdir("modules") if f.endswith(".py")]


# 🔥 считаем лучший по среднему
def get_best_module(experience):
    stats = {}

    for exp in experience:
        if isinstance(exp, dict):
            m = exp.get("module")
            s = exp.get("score", 0)

            stats.setdefault(m, []).append(s)

    best_module = None
    best_score = 0

    for m, scores in stats.items():
        avg = sum(scores) / len(scores)
        if avg > best_score:
            best_score = avg
            best_module = m

    return best_module, int(best_score)


# 🔥 генерация нового модуля
def create_new_module():
    modules = get_all_modules()
    new_id = len(modules) + 1
    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"""def run(data):
    data["log"].append("module {new_id} executed")
    return data
""")

    return name.replace(".py", "")


def execution(data):
    print("EXECUTION:", data["result"])

    os.makedirs("modules", exist_ok=True)

    module_used = None

    best_module, best_score = get_best_module(data.get("experience", []))

    # 🔥 СОЗДАНИЕ (теперь настоящее)
    if data["decision"] == "add_module":
        module_used = create_new_module()
        print(f"🔥 Создан модуль: {module_used}")
        data["result"] = "module created"

    # 🛠 УЛУЧШЕНИЕ (усиливаем лучший)
    elif data["decision"] == "improve_module":
        if best_module:
            path = os.path.join("modules", best_module + ".py")
            module_used = best_module

            with open(path, "a", encoding="utf-8") as f:
                f.write("\n# improved\n")

            print(f"🛠 Улучшен: {best_module}")
            data["result"] = "module improved"
        else:
            data["result"] = "no module to improve"

    # 🔄 АЛЬТЕРНАТИВА = новый модуль
    elif data["decision"] == "create_alternative":
        module_used = create_new_module()
        print(f"🔄 Альтернатива: {module_used}")
        data["result"] = "alternative created"

    # 🚀 ЗАПУСК
    elif data["decision"] == "run_module":

        if best_module:
            module_used = best_module
        else:
            modules = get_all_modules()
            if modules:
                module_used = modules[0].replace(".py", "")

        if module_used:
            path = os.path.join("modules", module_used + ".py")
            print(f"🚀 Запуск: {module_used}")
            data = run_python_module(path, data)
            data["result"] = "module executed"
        else:
            data["result"] = "no module to run"

    else:
        print("❌ Нет действия")
        data["result"] = "no action"

    # 🧠 ПАМЯТЬ
    data["memory"].append(data["decision"])
    if len(data["memory"]) > 100:
        data["memory"] = data["memory"][-100:]

    # 🧠 ОПЫТ
    if "experience" not in data:
        data["experience"] = []

    score = data.get("evaluation", {}).get("score", 50)

    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score
        })

        if len(data["experience"]) > 100:
            data["experience"] = data["experience"][-100:]

    data["log"].append(
        f"execution complete (used: {module_used}, best: {best_module})"
    )

    save_to_memory(data)

    return data
