import os
import importlib.util
import random


# 💾 безопасное сохранение
def save_to_memory(data):
    try:
        with open("memory.txt", "a", encoding="utf-8") as f:
            f.write(str(data) + "\n")
    except:
        pass


# 🚀 запуск модуля
def run_python_module(module_path, data):
    try:
        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            return module.run(data)
        else:
            data["log"].append("⚠️ module has no run()")
            return data

    except Exception as e:
        data["log"].append(f"❌ module error: {e}")
        return data


# 📁 список модулей
def get_all_modules():
    if not os.path.exists("modules"):
        return []
    return [f for f in os.listdir("modules") if f.endswith(".py")]


# 🧠 лучший модуль (по среднему)
def get_best_module(experience):
    stats = {}

    for exp in experience:
        if isinstance(exp, dict):
            m = exp.get("module")
            s = exp.get("score", 0)
            if m:
                stats.setdefault(m, []).append(s)

    best_module = None
    best_score = 0

    for m, scores in stats.items():
        if not scores:
            continue

        avg = sum(scores) / len(scores)

        if avg > best_score:
            best_score = avg
            best_module = m

    return best_module, int(best_score)


# 🧹 удаление слабых (с защитой лучшего)
def cleanup_modules(experience, best_module):
    stats = {}

    for exp in experience:
        if isinstance(exp, dict):
            m = exp.get("module")
            s = exp.get("score", 0)
            if m:
                stats.setdefault(m, []).append(s)

    for m, scores in stats.items():
        if m == best_module:
            continue  # 🔥 НЕ УДАЛЯЕМ ЛУЧШИЙ

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


# 🔥 создание модуля
def create_new_module():
    modules = get_all_modules()

    # 🔥 ограничение (анти-помойка)
    if len(modules) > 50:
        return None, "limit"

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
    data["goal"]["progress"] = data["goal"].get("progress", 0) + 5
    return data
"""
    elif module_type == "safe":
        code = f"""def run(data):
    data["log"].append("module {new_id} safe")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + 2
    return data
"""
    elif module_type == "explorer":
        code = f"""def run(data):
    data["log"].append("module {new_id} exploring")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + 3
    return data
"""
    else:
        code = f"""def run(data):
    data["log"].append("module {new_id} optimizing")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + 4
    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", ""), module_type


def execution(data):
    print("EXECUTION:", data.get("result"))

    os.makedirs("modules", exist_ok=True)

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    module_used = None

    best_module, best_score = get_best_module(data.get("experience", []))

    # 🚀 СОЗДАНИЕ
    if data["decision"] == "add_module":
        module_used, m_type = create_new_module()

        if module_used:
            print(f"🔥 Создан модуль: {module_used} ({m_type})")
            data["result"] = "module created"
        else:
            data["result"] = "module limit reached"

    # 🛠 УЛУЧШЕНИЕ
    elif data["decision"] == "improve_module":
        if best_module:
            path = os.path.join("modules", best_module + ".py")
            module_used = best_module

            if os.path.exists(path):
                try:
                    with open(path, "a", encoding="utf-8") as f:
                        f.write("\n# improved\n")

                    print(f"🛠 Улучшен: {best_module}")
                    data["result"] = "module improved"
                except:
                    data["result"] = "improve failed"
            else:
                data["result"] = "module missing"
        else:
            data["result"] = "no module to improve"

    # 🔄 АЛЬТЕРНАТИВА
    elif data["decision"] == "create_alternative":
        module_used, m_type = create_new_module()

        if module_used:
            print(f"🔄 Альтернатива: {module_used} ({m_type})")
            data["result"] = "alternative created"
        else:
            data["result"] = "module limit reached"

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

            if os.path.exists(path):
                print(f"🚀 Запуск: {module_used}")
                data = run_python_module(path, data)
                data["result"] = "module executed"
            else:
                data["result"] = "module not found"
        else:
            data["result"] = "no module to run"

    # 💡 ИДЕИ
    elif data["decision"] == "generate_idea":
        idea = f"Strategy idea: {data.get('task')}"

        data.setdefault("ideas", [])
        data["ideas"].append(idea)

        print("💡 Идея:", idea)

        if len(data["ideas"]) >= 3:
            module_used, m_type = create_new_module()

            if module_used:
                print(f"🧠 Идея → модуль: {module_used} ({m_type})")
                data["ideas"] = []
                data["result"] = "idea converted to module"
            else:
                data["result"] = "module limit reached"
        else:
            data["result"] = "idea generated"

    else:
        data["result"] = "no action"

    # 🧠 ПАМЯТЬ
    data["memory"].append(data["decision"])
    if len(data["memory"]) > 100:
        data["memory"] = data["memory"][-100:]

    # 🧠 ОПЫТ
    score = data.get("evaluation", {}).get("score", 50)

    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score
        })

        if len(data["experience"]) > 100:
            data["experience"] = data["experience"][-100:]

    # 🔥 ОЧИСТКА
    cleanup_modules(data.get("experience", []), best_module)

    data["log"].append(
        f"execution complete (used: {module_used}, best: {best_module}, best_score: {best_score})"
    )

    save_to_memory(data)

    return data
