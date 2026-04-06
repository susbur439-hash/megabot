import os
import importlib.util
import random


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


# 🔥 список модулей
def get_all_modules():
    if not os.path.exists("modules"):
        return []
    return [f for f in os.listdir("modules") if f.endswith(".py")]


# 🔥 лучший модуль (по среднему)
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


# 🔥 УДАЛЕНИЕ СЛАБЫХ МОДУЛЕЙ (LEVEL 6)
def cleanup_modules(experience):
    stats = {}

    for exp in experience:
        if isinstance(exp, dict):
            m = exp.get("module")
            s = exp.get("score", 0)
            stats.setdefault(m, []).append(s)

    for m, scores in stats.items():
        if len(scores) < 3:
            continue

        avg = sum(scores) / len(scores)

        if avg < 50:
            path = os.path.join("modules", m + ".py")

            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"🗑 Удален слабый модуль: {m} (avg={int(avg)})")
                except Exception as e:
                    print(f"⚠️ Ошибка удаления {m}:", e)


# 🔥 создание нового модуля
def create_new_module():
    modules = get_all_modules()
    new_id = len(modules) + 1

    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    module_type = random.choice([
        "aggressive",
        "safe",
        "explorer",
        "optimizer"
    ])

    if module_type == "aggressive":
        code = f"""def run(data):
    data["log"].append("module {new_id} aggressive")
    data["goal"]["progress"] += 5
    return data
"""
    elif module_type == "safe":
        code = f"""def run(data):
    data["log"].append("module {new_id} safe")
    data["goal"]["progress"] += 2
    return data
"""
    elif module_type == "explorer":
        code = f"""def run(data):
    data["log"].append("module {new_id} exploring")
    data["goal"]["progress"] += 3
    return data
"""
    else:
        code = f"""def run(data):
    data["log"].append("module {new_id} optimizing")
    data["goal"]["progress"] += 4
    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"🧠 Создан модуль {new_id} типа: {module_type}")

    return name.replace(".py", "")


def execution(data):
    print("EXECUTION:", data["result"])

    os.makedirs("modules", exist_ok=True)

    module_used = None

    best_module, best_score = get_best_module(data.get("experience", []))

    # 🚀 СОЗДАНИЕ
    if data["decision"] == "add_module":
        module_used = create_new_module()
        print(f"🔥 Создан модуль: {module_used}")
        data["result"] = "module created"

    # 🛠 УЛУЧШЕНИЕ
    elif data["decision"] == "improve_module":
        if best_module:
            path = os.path.join("modules", best_module + ".py")
            module_used = best_module

            try:
                with open(path, "a", encoding="utf-8") as f:
                    f.write("\n# improved\n")
                print(f"🛠 Улучшен: {best_module}")
                data["result"] = "module improved"
            except Exception as e:
                print("⚠️ Ошибка улучшения:", e)
                data["result"] = "improve failed"
        else:
            data["result"] = "no module to improve"

    # 🔄 АЛЬТЕРНАТИВА
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

    # 💡 ИДЕИ
    elif data["decision"] == "generate_idea":
        idea = f"Strategy idea based on task: {data['task']}"

        if "ideas" not in data:
            data["ideas"] = []

        data["ideas"].append(idea)

        print("💡 Идея:", idea)

        if len(data["ideas"]) >= 3:
            module_used = create_new_module()
            print(f"🧠 Идея превращена в модуль: {module_used}")
            data["ideas"] = []
            data["result"] = "idea converted to module"
        else:
            data["result"] = "idea generated"

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

    # 🔥 ЭВОЛЮЦИЯ (ОЧИСТКА)
    cleanup_modules(data.get("experience", []))

    data["log"].append(
        f"execution complete (used: {module_used}, best: {best_module})"
    )

    save_to_memory(data)

    return data
