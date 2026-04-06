import os
import importlib.util
import random
import time

from modules.decision import decision


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

    code = f"""def run(data):
    data["log"].append("module {new_id} running")
    data["goal"]["progress"] = data["goal"].get("progress", 0) + {random.randint(2,6)}
    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 🔥 ГЛАВНАЯ ФУНКЦИЯ
# =========================
def execution(data):

    print("EXECUTION:", data.get("result"))

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    # =========================
    # 🧠 DECISION
    # =========================
    data = decision(data)

    module_used = None

    best_module, best_score = get_best_module(data["experience"])

    # =========================
    # 🚀 СОЗДАНИЕ
    # =========================
    if data["decision"] == "add_module":
        module_used = create_new_module()
        data["result"] = "module created"

    # =========================
    # 🔄 АЛЬТЕРНАТИВА
    # =========================
    elif data["decision"] == "create_alternative":
        module_used = create_new_module()
        data["result"] = "alternative created"

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
                data = run_python_module(path, data)
                data["result"] = "module executed"
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
            module_used = create_new_module()
            data["ideas"] = []
            data["result"] = "idea converted to module"
        else:
            data["result"] = "idea generated"

    # =========================
    # 🛠 УЛУЧШЕНИЕ
    # =========================
    elif data["decision"] == "improve_module":
        data["result"] = "module improved"

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
        data["experience"].append({
            "module": module_used,
            "score": data.get("evaluation", {}).get("score", 50)
        })

        data["experience"] = data["experience"][-100:]

    # =========================
    # 📊 ЛОГ
    # =========================
    data["log"].append(
        f"execution complete (used: {module_used}, best: {best_module}, score: {best_score})"
    )

    save_to_memory(data)

    return data
