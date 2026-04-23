def run(task_data):
    """
    Task Interpreter:
    превращает сырую задачу в структурированный план
    """

    task = task_data.get("task", "")

    result = {
        "original_task": task,
        "type": None,
        "priority": "normal",
        "steps": [],
        "goal": None
    }

    # =========================
    # 🧠 ОПРЕДЕЛЕНИЕ ТИПА ЗАДАЧИ
    # =========================
    if "развивай" in task or "развитие" in task:
        result["type"] = "self_improvement"
        result["goal"] = "improve_system"

        result["steps"] = [
            "анализ текущего состояния",
            "поиск слабых мест",
            "создание недостающих модулей",
            "оптимизация логики"
        ]

    elif "исправь" in task or "fix" in task:
        result["type"] = "fix"
        result["priority"] = "high"

        result["steps"] = [
            "найти ошибку",
            "проанализировать причину",
            "создать патч",
            "проверить систему"
        ]

    elif "создай" in task or "create" in task:
        result["type"] = "creation"

        result["steps"] = [
            "понять что нужно создать",
            "определить зависимости",
            "создать модуль",
            "интегрировать в систему"
        ]

    else:
        result["type"] = "general"

        result["steps"] = [
            "проанализировать задачу",
            "разбить на подзадачи",
            "выбрать стратегию выполнения"
        ]

    # =========================
    # 🔥 УЛУЧШЕНИЕ ПРИОРИТЕТА
    # =========================
    if "crash" in task or "error" in task:
        result["priority"] = "critical"

    return result
