def run(data):
    """
    Task Interpreter:
    превращает задачу в структурированное представление
    и записывает его в data
    """

    task = str(data.get("task", "")).lower()

    result = {
        "original_task": task,
        "type": None,
        "priority": "normal",
        "steps": [],
        "goal": None
    }

    # =========================
    # 🧠 ОПРЕДЕЛЕНИЕ ТИПА
    # =========================
    if "развивай" in task or "развитие" in task:
        result["type"] = "self_improvement"
        result["goal"] = "improve_system"

        result["steps"] = [
            "analyze_system",
            "find_weak_points",
            "improve_modules",
            "optimize_logic"
        ]

    elif "исправь" in task or "fix" in task:
        result["type"] = "fix"
        result["priority"] = "high"

        result["steps"] = [
            "detect_error",
            "analyze_cause",
            "create_fix",
            "test_system"
        ]

    elif "создай" in task or "create" in task:
        result["type"] = "creation"

        result["steps"] = [
            "understand_goal",
            "define_dependencies",
            "build_module",
            "integrate"
        ]

    else:
        result["type"] = "general"

        result["steps"] = [
            "analyze_task",
            "split_into_steps",
            "choose_strategy"
        ]

    # =========================
    # 🔥 ПРИОРИТЕТ
    # =========================
    if "crash" in task or "error" in task:
        result["priority"] = "critical"

    # =========================
    # 📦 СОХРАНЕНИЕ В DATA
    # =========================
    data["task_struct"] = result

    # быстрый доступ
    data["task_type"] = result["type"]
    data["task_priority"] = result["priority"]

    data.setdefault("log", []).append(
        f"🧠 task: {result['type']} | priority: {result['priority']}"
    )

    return data


# =========================
# 🔥 ДОПОЛНИТЕЛЬНО (если нужно)
# =========================
def interpret(task: str):
    """
    Упрощённый интерфейс (оставляем, но не основной)
    """

    structured = run({"task": task})
    return structured.get("task_struct", {})
