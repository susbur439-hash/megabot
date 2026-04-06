import os
import importlib.util
import random


# =========================
# 💾 СОХРАНЕНИЕ
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
# 🧠 ЛУЧШИЙ МОДУЛЬ
# =========================
def get_best_module(experience):
    best_module = None
    best_score = 0

    for exp in experience:
        if isinstance(exp, dict):
            score = exp.get("score", 0)
            module = exp.get("module")

            if score > best_score:
                best_score = score
                best_module = module

    return best_module, best_score


# =========================
# 🧠 СОЗДАНИЕ МОДУЛЯ
# =========================
def create_new_module():
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()
    new_id = len(modules) + 1

    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    boost = random.randint(2, 8)

    code = f"""def run(data):
    data["log"].append("module {new_id} running (boost {boost})")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + {boost}
    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 📊 РЕАЛЬНАЯ ОЦЕНКА
# =========================
def calculate_score(before, after):
    delta = after - before

    score = delta * 10 + random.randint(0, 5)

    return max(0, min(100, score))


# =========================
# 🔁 ПРОВЕРКА ЗАСТРЕВАНИЯ
# =========================
def is_stuck(memory):
    if len(memory) < 5:
        return False

    last = memory[-5:]
    return len(set(last)) == 1  # все одинаковые


# =========================
# 🔥 ГЛАВНАЯ ФУНКЦИЯ
# =========================
def execution(data):

    print("EXECUTION:", data.get("result"))

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    module_used = None
    real_score = None

    best_module, best_score = get_best_module(data["experience"])

    # =========================
    # 🚀 СОЗДАНИЕ + ТЕСТ
    # =========================
    if data["decision"] == "add_module":
        module_used = create_new_module()

        path = os.path.join("modules", module_used + ".py")

        before = data["goal"].get("progress", 0)

        data = run_python_module(path, data)

        after = data["goal"].get("progress", 0)

        real_score = calculate_score(before, after)

        data["result"] = f"module created & tested ({real_score})"

    # =========================
    # 🔄 АЛЬТЕРНАТИВА
    # =========================
    elif data["decision"] == "create_alternative":
        module_used = create_new_module()
        data["result"] = "alternative created"
        real_score = 50

    # =========================
    # 🚀 ЗАПУСК
    # =========================
    elif data["decision"] == "run_module":

        # 🔥 если застряли — не используем лучший
        if is_stuck(data["memory"]):
            modules = get_all_modules()
            if modules:
                module_used = random.choice(modules).replace(".py", "")
                data["log"].append("⚠️ anti-stuck: random module selected")
        else:
            module_used = best_module

        if not module_used:
            modules = get_all_modules()
            if modules:
                module_used = modules[0].replace(".py", "")

        if module_used:
            path = os.path.join("modules", module_used + ".py")

            if os.path.exists(path):
                before = data["goal"].get("progress", 0)

                data = run_python_module(path, data)

                after = data["goal"].get("progress", 0)

                real_score = calculate_score(before, after)

                data["result"] = f"module executed ({real_score})"
            else:
                data["result"] = "module missing"
        else:
            data["result"] = "no module to run"

    # =========================
    # 💡 ИДЕИ
    # =========================
    elif data["decision"] == "generate_idea":

        idea = f"Strategy: {data.get('task')}"
        data.setdefault("ideas", [])
        data["ideas"].append(idea)

        if len(data["ideas"]) >= 3:
            if len(get_all_modules()) < 20:
                module_used = create_new_module()

                # 🔥 сразу тест
                path = os.path.join("modules", module_used + ".py")

                before = data["goal"].get("progress", 0)
                data = run_python_module(path, data)
                after = data["goal"].get("progress", 0)

                real_score = calculate_score(before, after)

                data["ideas"] = []
                data["result"] = f"idea → module ({real_score})"
            else:
                data["result"] = "too many modules"
        else:
            data["result"] = "idea generated"

    # =========================
    # 🛠 УЛУЧШЕНИЕ
    # =========================
    elif data["decision"] == "improve_module":
        data["result"] = "module improved"
        real_score = 65

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
    if module_used:
        if real_score is None:
            real_score = 50

        # 🔥 штраф за повтор
        if module_used == best_module:
            real_score -= 5

        data["experience"].append({
            "module": module_used,
            "score": max(0, real_score)
        })

        data["experience"] = data["experience"][-100:]

    # =========================
    # 📊 ЛОГ
    # =========================
    data["log"].append(
        f"execution complete (used: {module_used}, best: {best_module}, best_score: {best_score}, new_score: {real_score})"
    )

    save_to_memory(data)

    return data
