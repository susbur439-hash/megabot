import json
import os


def decide(task: str, engine_result=None, router_state=None, brain_map=None):
    """
    🧠 CENTRAL BRAIN v2 (UPGRADED)

    Теперь:
    - учитывает brain_map
    - оценивает хаос
    - определяет здоровье системы
    - принимает системные решения
    """

    task_lower = str(task).lower()

    # =========================
    # 🧠 1. SYSTEM ANALYSIS (brain_map)
    # =========================
    chaos_score = 0

    if brain_map:
        try:
            layers = brain_map.get("layers", {})
            imports = brain_map.get("imports", {})
            orphans = brain_map.get("orphans", [])

            # overload detection
            for layer, modules in layers.items():
                if len(modules) > 200:
                    chaos_score += 25

            # orphan penalty
            chaos_score += len(orphans) * 3

            # dependency overload
            for _, deps in imports.items():
                if len(deps) > 20:
                    chaos_score += 2

        except Exception:
            pass

    # =========================
    # 🔴 2. EMERGENCY OVERRIDE
    # =========================
    if chaos_score > 60:
        return {
            "mode": "system_repair",
            "reason": "high_chaos_detected",
            "chaos_score": chaos_score
        }

    # =========================
    # 🔧 3. TECH TASKS
    # =========================
    tech_keywords = [
        "system", "list", "status", "modules",
        "engine", "check", "scan", "map"
    ]

    if any(k in task_lower for k in tech_keywords):
        return {
            "mode": "engine",
            "reason": "technical_task",
            "chaos_score": chaos_score
        }

    # =========================
    # 🧠 4. ENGINE CONFIRMATION
    # =========================
    if engine_result:
        if isinstance(engine_result, dict):
            if engine_result.get("status") == "ok":
                return {
                    "mode": "engine",
                    "reason": "engine_confirms",
                    "chaos_score": chaos_score
                }

    # =========================
    # 🔀 5. COMPLEX SYSTEM ROUTING
    # =========================
    if router_state:
        if router_state.get("modules_loaded", 0) > 100:
            return {
                "mode": "director",
                "reason": "complex_system",
                "chaos_score": chaos_score
            }

    # =========================
    # 🟢 DEFAULT
    # =========================
    return {
        "mode": "director",
        "reason": "default_fallback",
        "chaos_score": chaos_score
    }
