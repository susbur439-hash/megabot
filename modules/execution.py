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
# 🧠 ЛУЧШИЕ МОДУЛИ (ТОП)
# =========================
def get_top_modules(experience, n=3):
    valid = [e for e in experience if isinstance(e, dict)]
    sorted_exp = sorted(valid, key=lambda x: x.get("score", 0), reverse=True)
    return sorted_exp[:n]


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
# 🧬 СОЗДАНИЕ МОДУЛЯ (ЭВОЛЮЦИЯ)
# =========================
def create_new_module(parent=None):
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()
    new_id = len(modules) + 1

    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    if parent and isinstance(parent, dict):
        base_boost = parent.get("boost", 5)
        boost = max(1, int(base_boost + random.randint(-2, 3)))
    else:
        boost = random.randint(2, 10)

    behavior = random.choice(["aggressive", "balanced", "safe"])

    code = f"""def run(data):
    boost = {boost}
    behavior = "{behavior}"

    if behavior == "aggressive":
        boost *= 1.5
    elif behavior == "safe":
        boost *= 0.7

    boost = int(boost)

    data["log"].append(f"module {new_id} | behavior={{behavior}} | boost={{boost}}")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + boost

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return {
        "name": name.replace(".py", ""),
        "boost": boost,
        "behavior": behavior
    }


# =========================
# 📊 ОЦЕНКА
# =========================
def calculate_score(before, after):
    delta = after - before
    score = delta * 10 + random.randint(-5, 5)
    return max(0, min(100, score))


# =========================
# 🧹 УДАЛЕНИЕ СЛАБЫХ
# =========================
def cleanup_modules(data):
    if len(data["experience"]) < 5:
        return

    worst_module, worst_score = get_worst_module(data["experience"])

    if worst_score < 20 and worst_module:
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

    top_modules = get_top_modules(data["experience"])
    best_module = top_modules[0]["module"] if top_modules else None
    best_score = top_modules[0]["score"] if top_modules else 0

    explore = random.random() < 0.3  # 30% исследование

    # =========================
    # 🚀 СОЗДАНИЕ / ЭВОЛЮЦИЯ
    # =========================
    if data["decision"] == "add_module" or explore:

        parent = None
        if top_modules:
            parent = random.choice(top_modules)

        module_used = create_new_module(parent)
        module_name = module_used["name"]

        path = os.path.join("modules", module_name + ".py")

        before = data["goal"].get("progress", 0)
        data = run_python_module(path, data)
        after = data["goal"].get("progress", 0)

        real_score = calculate_score(before, after)
        data["result"] = f"module evolved & tested ({real_score})"

    # =========================
    # 🚀 ИСПОЛЬЗОВАНИЕ ЛУЧШЕГО
    # =========================
    elif data["decision"] == "run_module":

        if best_module:
            module_used = best_module

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
    # 🧠 ОПЫТ (УЛУЧШЕННЫЙ)
    # =========================
    if module_used:
        if isinstance(module_used, dict):
            module_name = module_used["name"]
        else:
            module_name = module_used

        if real_score is None:
            real_score = 50

        data["experience"].append({
            "module": module_name,
            "score": real_score,
            "time": len(data["memory"])
        })

        data["experience"] = sorted(
            data["experience"],
            key=lambda x: x["score"],
            reverse=True
        )[:100]

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
