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
# 📁 СПИСОК
# =========================
def get_all_modules():
    if not os.path.exists("modules"):
        return []
    return [f for f in os.listdir("modules") if f.endswith(".py")]


# =========================
# 🧠 ТОП МОДУЛИ
# =========================
def get_top_modules(experience, n=3):
    valid = [e for e in experience if isinstance(e, dict)]
    return sorted(valid, key=lambda x: x.get("score", 0), reverse=True)[:n]


# =========================
# 🧠 ХУДШИЙ
# =========================
def get_worst_module(experience):
    valid = [e for e in experience if isinstance(e, dict)]
    if not valid:
        return None, None

    worst = min(valid, key=lambda x: x.get("score", 0))
    return worst.get("module"), worst.get("score")


# =========================
# 🧬 СОЗДАНИЕ (МУТАЦИЯ)
# =========================
def create_new_module(parent=None):
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()
    new_id = len(modules) + 1

    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    # 🎯 наследование
    if parent:
        base = parent.get("score", 50)
        boost = max(1, int(base / 10 + random.randint(-3, 5)))
    else:
        boost = random.randint(2, 10)

    behavior = random.choice(["aggressive", "balanced", "safe"])

    code = f"""def run(data):
    boost = {boost}
    behavior = "{behavior}"

    if behavior == "aggressive":
        boost *= 1.6
    elif behavior == "safe":
        boost *= 0.6

    boost = int(boost)

    data["log"].append(f"module {new_id} | behavior={{behavior}} | boost={{boost}}")

    # 🎯 влияние на цель
    data["goal"]["progress"] = data["goal"].get("progress", 0) + boost

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 📊 СКОРА
# =========================
def calculate_score(before, after):
    delta = after - before
    score = delta * 10 + random.randint(-5, 5)
    return max(0, min(100, score))


# =========================
# 🛠 УЛУЧШЕНИЕ (РЕАЛЬНОЕ)
# =========================
def improve_existing_module(module_name):
    path = os.path.join("modules", module_name + ".py")

    if not os.path.exists(path):
        return False

    # простая мутация — усиливаем код
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    code = code.replace("boost =", "boost = int(")
    code = code.replace("return data", "boost += 1\n    return data")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return True


# =========================
# 🧹 ЧИСТКА (ЖЁСТЧЕ)
# =========================
def cleanup_modules(data):
    if len(data["experience"]) < 5:
        return

    worst_module, worst_score = get_worst_module(data["experience"])

    if worst_score is not None and worst_score < 30:
        path = os.path.join("modules", worst_module + ".py")

        if os.path.exists(path):
            os.remove(path)
            data["log"].append(f"🗑 removed weak module: {worst_module}")


# =========================
# 🔥 EXECUTION
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

    explore = random.random() < 0.25

    # =========================
    # 🚀 СОЗДАНИЕ / ЭВОЛЮЦИЯ
    # =========================
    if data["decision"] == "add_module" or explore:

        parent = random.choice(top_modules) if top_modules else None

        module_used = create_new_module(parent)

        path = os.path.join("modules", module_used + ".py")

        before = data["goal"].get("progress", 0)
        data = run_python_module(path, data)
        after = data["goal"].get("progress", 0)

        real_score = calculate_score(before, after)
        data["result"] = f"module evolved & tested ({real_score})"

    # =========================
    # 🚀 ЗАПУСК
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
    # 💡 ИДЕИ → СРАЗУ В МОДУЛЬ
    # =========================
    elif data["decision"] == "generate_idea":

        parent = random.choice(top_modules) if top_modules else None
        module_used = create_new_module(parent)

        data["result"] = "idea → module"

    # =========================
    # 🛠 УЛУЧШЕНИЕ
    # =========================
    elif data["decision"] == "improve_module":

        if best_module and improve_existing_module(best_module):
            module_used = best_module
            real_score = best_score + 10
            data["result"] = "module improved (real)"

        else:
            data["result"] = "improve failed"

    # =========================
    # ❌ FALLBACK
    # =========================
    else:
        data["result"] = "no action"

    # =========================
    # 🧠 MEMORY
    # =========================
    data["memory"].append(data["decision"])
    data["memory"] = data["memory"][-100:]

    # =========================
    # 🧠 EXPERIENCE
    # =========================
    if module_used:
        if real_score is None:
            real_score = 50

        data["experience"].append({
            "module": module_used,
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
    # 📊 LOG
    # =========================
    data["log"].append(
        f"execution complete (used: {module_used}, best: {best_module}, best_score: {best_score}, new_score: {real_score})"
    )

    save_to_memory(data)

    return data
