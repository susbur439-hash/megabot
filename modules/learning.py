import json
import os


def run(context):
    """
    Learning module:
    накапливает опыт, анализирует прошлые результаты и улучшает стратегию
    """

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

    # =========================
    # 📊 ТЕКУЩИЙ РЕЗУЛЬТАТ
    # =========================
    score = context.get("evaluation", {}).get("score", 50)
    task = context.get("task", "unknown")

    modules_created = context.get("modules_created", [])

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
    # 💾 СОХРАНЕНИЕ ПАМЯТИ
    # =========================
    memory["experiences"] = experiences[-50:]  # ограничение памяти

    try:
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except:
        pass

    # =========================
    # 📤 РЕЗУЛЬТАТ
    # =========================
    return {
        "trend": trend,
        "insights": insights,
        "total_experiences": len(experiences)
    }
