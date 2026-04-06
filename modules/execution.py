import os
import importlib.util
import random
import time


# =========================
# 💾 БЕЗОПАСНОЕ СОХРАНЕНИЕ
# =========================
def save_to_memory(data):
    try:
        with open("memory.txt", "a", encoding="utf-8") as f:
            f.write(str(data) + "\n")
    except:
        pass


# =========================
# 🚀 ЗАПУСК МОДУЛЯ
# =========================
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


# =========================
# 📁 СПИСОК МОДУЛЕЙ
# =========================
def get_all_modules():
    if not os.path.exists("modules"):
        return []
    return [f for f in os.listdir("modules") if f.endswith(".py")]


# =========================
# 🧠 ЛУЧШИЙ МОДУЛЬ (СРЕДНЕЕ)
# =========================
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


# =========================
# 🧹 ОЧИСТКА (НЕ ТРОГАЕМ ЛУЧШИЙ)
# =========================
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
            continue

        if len(scores) < 3:
            continue

        avg = sum(scores) / len(scores)

        if avg < 50:
            path = os.path.join("modules", m + ".py")

            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"🗑 Удален слабый модуль: {m} (avg={int(avg)})")
                except:
                    pass


# =========================
# 🧠 СОЗДАНИЕ МОДУЛЯ (УЛУЧШЕНО)
# =========================
def create_new_module():
    modules = get_all_modules()

    # 🔥 ограничение
    if len(modules) > 50:
        return None, "limit"

    new_id = len(modules) + 1

    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    module_type = random.choice([
        "aggressive",
        "safe",
        "explorer",
        "optimizer",
        "balanced"
    ])

    code = ""

    if module_type == "aggressive":
        code = f"""def run(data):
    data["log"].append("module {new_id} aggressive")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + 6
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

    elif module_type == "optimizer":
        code = f"""def run(data):
    data["log"].append("module {new_id} optimizing")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + 4
    return data
"""

    else:  # balanced
        code = f"""def run(data):
    data["log"].append("module {new_id} balanced")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + 3
    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", ""), module_type


# =========================
# 🧠 ЗАЩИТА СИСТЕМЫ (ВАЖНО)
# =========================
def apply_system_rules(data):
    rules = [
        "Работать только в рамках законов РФ",
        "Не нарушать правила платформ",
        "Не выполнять опасные действия"
    ]

    data["system_rules"] = rules
    return data


# =========================
# 🔥 ГЛАВНАЯ ФУНКЦИЯ
# =========================
def execution(data):

    print("EXECUTION:", data.get("result"))

    os.makedirs("modules", exist_ok=True)

    # 🔒 защита структуры
    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    # 🔥 применяем правила
    data = apply_system_rules(data)

    module_used = None

    best_module, best_score = get_best_module(data["experience"])

    # =========================
    # 🚀 СОЗДАНИЕ
    # =========================
    if data["decision"] == "add_module":
        module_used, m_type = create_new_module()

        if module_used:
            print(f"🔥 Создан: {module_used} ({m_type})")
            data["result"] = "module created"
        else:
            data["result"] = "limit reached"

    # =========================
    # 🛠 УЛУЧШЕНИЕ
    # =========================
    elif data["decision"] == "improve_module":
        if best_module:
            path = os.path.join("modules", best_module + ".py")
            module_used = best_module

            if os.path.exists(path):
                try:
                    with open(path, "a", encoding="utf-8") as f:
                        f.write("\n# improved " + str(time.time()))
                    data["result"] = "module improved"
                except:
                    data["result"] = "improve failed"
        else:
            data["result"] = "no module"

    # =========================
    # 🔄 АЛЬТЕРНАТИВА
    # =========================
    elif data["decision"] == "create_alternative":
        module_used, m_type = create_new_module()

        if module_used:
            print(f"🔄 Новый путь: {module_used} ({m_type})")
            data["result"] = "alternative created"
        else:
            data["result"] = "limit reached"

    # =========================
    # 🚀 ЗАПУСК
    # =========================
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
                data["result"] = "module missing"

        else:
            data["result"] = "no module"

    # =========================
    # 💡 ИДЕИ → ЭВОЛЮЦИЯ
    # =========================
    elif data["decision"] == "generate_idea":

        idea = f"Strategy: {data.get('task')}"

        data.setdefault("ideas", [])
        data["ideas"].append(idea)

        print("💡", idea)

        if len(data["ideas"]) >= 3:
            module_used, m_type = create_new_module()

            if module_used:
                print(f"🧠 Идея → модуль: {module_used}")
                data["ideas"] = []
                data["result"] = "idea → module"
            else:
                data["result"] = "limit reached"
        else:
            data["result"] = "idea generated"

    # =========================
    # ❌ НИЧЕГО
    # =========================
    else:
        data["result"] = "no action"

    # =========================
    # 🧠 ПАМЯТЬ
    # =========================
    data["memory"].append(data["decision"])
    data["memory"] = data["memory"][-100:]

    # =========================
    # 🧠 ОПЫТ
    # =========================
    score = data.get("evaluation", {}).get("score", 50)

    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score
        })

        data["experience"] = data["experience"][-100:]

    # =========================
    # 🧹 ЧИСТКА
    # =========================
    cleanup_modules(data["experience"], best_module)

    # =========================
    # 📊 ЛОГ
    # =========================
    data["log"].append(
        f"execution complete (used: {module_used}, best: {best_module}, score: {best_score})"
    )

    save_to_memory(data)

    return data
