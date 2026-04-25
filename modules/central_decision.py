import json

# пробуем подключить оба ядра
try:
    from modules.director import run as director_run
except:
    director_run = None

try:
    from modules.engine import run as engine_run
except:
    engine_run = None


def decide_mode(task: str) -> str:
    """
    🧠 Улучшенная логика выбора системы
    (более стабильный роутинг)
    """

    task_lower = task.lower()

    engine_keywords = [
        "system", "list", "modules", "router", "status",
        "scan", "repo", "health", "debug", "logs"
    ]

    # 🟢 engine — только системные/технические команды
    if any(k in task_lower for k in engine_keywords):
        return "engine"

    # 🔴 всё остальное → director (мышление / развитие)
    return "director"


def run(task: str):
    """
    🚀 Единая точка входа в Megabot
    """

    mode = decide_mode(task)

    print(f"[CentralDecision] task='{task}' → mode={mode}")

    # 🟢 Engine слой
    if mode == "engine" and engine_run:
        print("[CentralDecision] → Engine selected")
        return engine_run(task)

    # 🔴 Director слой
    if director_run:
        print("[CentralDecision] → Director selected")
        return director_run(task)

    return {
        "status": "error",
        "message": "No execution layer available"
    }
