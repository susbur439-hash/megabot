import json
import os
import random


def run(context):
    """
    Learning module:
    накапливает опыт, анализирует прошлые результаты и улучшает стратегию
    + активное саморазвитие системы
    """

    print("[Learning] START")

    memory_file = "memory.json"

    # =========================
    # 📦 ЗАГРУЗКА ПАМЯТИ
    # =========================
    if os.path.exists(memory_file):
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                memory = json.load(f)
        except:
            memory = {"experiences": []}
    else:
        memory = {"experiences": []}

    experiences = memory.get("experiences", [])
    memory.setdefault("learning_log", [])

    # =========================
    # 📊 ТЕКУЩИЙ КОНТЕКСТ
    # =========================
    task = context.get("task", "unknown")
    meta = context.get("meta", {})

    score = context.get("evaluation", {}).get("score", 50)
    modules_created = context.get("modules_created", [])

    print(f"[Learning] Task: {task}")
    print(f"[Learning] Goal: {meta.get('goal')}")

    # =========================
    # 🧠 ЗАПИСЬ ОПЫТА
    # =========================
    experience = {
        "task": task,
        "score": score,
        "modules_created": modules_created,
        "success": score >= 70
    }

    experiences.append(experience)

    # =========================
    # 📈 АНАЛИЗ ТЕНДЕНЦИИ
    # =========================
    last_scores = [e["score"] for e in experiences[-10:]]

    trend = "stable"

    if len(last_scores) >= 3:
        if last_scores[-1] > last_scores[0]:
            trend = "improving"
        elif last_scores[-1] < last_scores[0]:
            trend = "declining"

    # =========================
    # 🧠 ВЫВОД ОБУЧЕНИЯ
    # =========================
    insights = []

    if trend == "improving":
        insights.append("system is improving strategy")
    elif trend == "declining":
        insights.append("system is degrading performance")

    if len(modules_created) > 3:
        insights.append("too many modules created per cycle")

    if score < 40:
        insights.append("low quality output detected")

    # =========================
    # 🔥 АКТИВНОЕ САМООБУЧЕНИЕ
    # =========================
    created_module = None

    # если задача — саморазвитие → создаём модуль
    if meta.get("goal") == "improve_system":
        modules_dir = "modules"
        os.makedirs(modules_dir, exist_ok=True)

        new_module_name = f"module_auto_{random.randint(1000,9999)}.py"
        new_module_path = os.path.join(modules_dir, new_module_name)

        if not os.path.exists(new_module_path):
            with open(new_module_path, "w", encoding="utf-8") as f:
                f.write(f'''
def run(data):
    print("🚀 Auto-generated module working")
    return {{"status": "ok"}}
''')

            print(f"[Learning] Created new module: {new_module_name}")
            created_module = new_module_name

    # =========================
    # 💾 ЛОГ ОБУЧЕНИЯ
    # =========================
    memory["learning_log"].append({
        "task": task,
        "trend": trend,
        "insights": insights,
        "created_module": created_module
    })

    # =========================
    # 💾 СОХРАНЕНИЕ ПАМЯТИ
    # =========================
    memory["experiences"] = experiences[-50:]

    try:
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except:
        pass

    print("[Learning] DONE")

    # =========================
    # 📤 РЕЗУЛЬТАТ
    # =========================
    return {
        "status": "ok",
        "trend": trend,
        "insights": insights,
        "created_module": created_module,
        "total_experiences": len(experiences)
    }
