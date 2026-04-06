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
# 🧠 ХУДШИЙ МОДУЛЬ
# =========================
def get_worst_module(experience):
    worst_module = None
    worst_score = 999

    for exp in experience:
        if isinstance(exp, dict):
            score = exp.get("score", 0)
            module = exp.get("module")

            if score < worst_score:
                worst_score = score
                worst_module = module

    return worst_module, worst_score


# =========================
# 🧠 СОЗДАНИЕ МОДУЛЯ
# =========================
def create_new_module():
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()
    new_id = len(modules) + 1

    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    boost = random.randint(1, 10)

    code = f"""def run(data):
    boost = {boost}
    data["log"].append(f"module {new_id} running (boost {{boost}})")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + boost
    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 📊 ОЦЕНКА
# =========================
def calculate_score(before, after):
    delta = after - before

    score = delta * 10

    # шум (чтобы не было одинаково)
    score += random.randint(-5, 5)

    return max(0, min(100, score))


# =========================
# 🧹 УДАЛЕНИЕ СЛАБЫХ МОДУЛЕЙ
# =========================
def cleanup_modules(data):
    if len(data["experience"]) < 5:
        return

    worst_module, worst_score = get_worst_module(data["experience"])

    if worst_score < 20:
        path = os.path.join("modules", worst_module + ".py")

        if os.path.exists(path):
            os.remove(path)
            data["log"].append(f"🗑 removed weak module: {worst_module}")


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
    # 🧠 РЕЖИМ: ИССЛЕДОВАНИЕ / ИСПОЛЬЗОВАНИЕ
    # =========================
    explore = random.random() < 0.3  # 30% исследует

    # =========================
    # 🚀 СОЗДАНИЕ
    # =========================
    if data["decision"] == "add_module" or explore:
        module_used = create_new_module()
        data["result"] = "module created"

        # сразу тестим
        path = os.path.join("modules", module_used + ".py")

        before = data["goal"].get("progress", 0)
        data = run_python_module(path, data)
        after = data["goal"].get("progress", 0)

        real_score = calculate_score(before, after)
        data["result"] += f" & tested ({real_score})"

    # =========================
    # 🚀 ЗАПУСК ЛУЧШЕГО
    # =========================
    elif data["decision"] == "run_module":

        if best_module:
            module_used = best_module

        if module_used:
            path = os.path.join("modules", module_used + ".py")

            before = data["goal"].get("progress", 0)
            data = run_python_module(path, data)
            after = data["goal"].get("progress", 0)

            real_score = calculate_score(before, after)
            data["result"] = f"best module executed ({real_score})"

    # =========================
    # 💡 ИДЕИ
    # =========================
    elif data["decision"] == "generate_idea":
        idea = f"Strategy: {data.get('task')}"
        data.setdefault("ideas", [])
        data["ideas"].append(idea)

        data["result"] = "idea generated"

    # =========================
    # 🛠 УЛУЧШЕНИЕ
    # =========================
    elif data["decision"] == "improve_module":
        data["result"] = "module improved"
        real_score = best_score + 5

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

        data["experience"].append({
            "module": module_used,
            "score": real_score
        })

        data["experience"] = data["experience"][-100:]

    # =========================
    # 🧹 ЧИСТКА
    # =========================
    cleanup_modules(data)

    # =========================
    # 📊 ЛОГ
    # =========================
    data["log"].append(
        f"execution complete (used: {module_used}, best: {best_module}, best_score: {best_score}, new_score: {real_score})"
    )

    save_to_memory(data)

    return data
