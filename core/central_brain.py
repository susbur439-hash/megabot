def decide(task: str, engine_result=None, router_state=None):
    """
    🧠 CENTRAL BRAIN v1
    ЕДИНАЯ ТОЧКА ПРИНЯТИЯ РЕШЕНИЙ
    """

    task_lower = str(task).lower()

    # =========================
    # 🔧 1. ТЕХНИЧЕСКИЕ ЗАДАЧИ → ENGINE
    # =========================
    tech_keywords = [
        "system", "list", "status", "modules",
        "engine", "check", "scan", "map"
    ]

    if any(k in task_lower for k in tech_keywords):
        return {
            "mode": "engine",
            "reason": "technical_task"
        }

    # =========================
    # 🧠 2. ЕСЛИ ENGINE УЖЕ ДАЛ РЕЗУЛЬТАТ
    # =========================
    if engine_result:
        if isinstance(engine_result, dict):
            if engine_result.get("status") == "ok":
                return {
                    "mode": "engine",
                    "reason": "engine_confirms"
                }

    # =========================
    # 🔀 3. ЕСЛИ РОУТЕР АКТИВЕН И СИСТЕМА СТАБИЛЬНА
    # =========================
    if router_state:
        if router_state.get("modules_loaded", 0) > 100:
            return {
                "mode": "director",
                "reason": "complex_logic"
            }

    # =========================
    # 🔴 4. DEFAULT
    # =========================
    return {
        "mode": "director",
        "reason": "default_fallback"
    }
