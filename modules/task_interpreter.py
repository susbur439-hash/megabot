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
    if "развивай" in task.lower() or "развитие" in task.lower():
        result["type"] = "self_improvement"
        result["goal"] = "improve_system"

        result["steps"] = [
            "анализ текущего состояния",
            "поиск слабых мест",
            "создание недостающих модулей",
            "оптимизация логики"
        ]

    elif "исправь" in task.lower() or "fix" in task.lower():
        result["type"] = "fix"
        result["priority"] = "high"

        result["steps"] = [
            "найти ошибку",
            "проанализировать причину",
            "создать патч",
            "проверить систему"
        ]

    elif "создай" in task.lower() or "create" in task.lower():
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
    if "crash" in task.lower() or "error" in task.lower():
        result["priority"] = "critical"

    return result


# =========================
# 🔥 НОВОЕ: ENGINE INTERFACE
# =========================
def interpret(task: str):
    """
    Преобразует задачу в команду для Engine
    """

    print(f"[TaskInterpreter] Received task: {task}")

    structured = run({"task": task})

    task_type = structured.get("type")

    # =========================
    # 🎯 МАППИНГ В ENGINE
    # =========================
    if task_type == "self_improvement":
        command = {
            "module": "learning",
            "action": "self_improve",
            "task": task,
            "meta": structured
        }

    elif task_type == "fix":
        command = {
            "module": "system",
            "action": "fix",
            "task": task,
            "meta": structured
        }

    elif task_type == "creation":
        command = {
            "module": "planning",
            "action": "create",
            "task": task,
            "meta": structured
        }

    else:
        command = {
            "module": "system",
            "action": "list",
            "task": task,
            "meta": structured
        }

    print(f"[TaskInterpreter] Interpreted as: {command}")

    return command
