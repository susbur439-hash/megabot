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
    🧠 Простая логика выбора системы
    """

    task_lower = task.lower()

    # Engine-режим (новая система управления)
    if any(keyword in task_lower for keyword in [
        "system", "list", "modules", "router", "status"
    ]):
        return "engine"

    # Director-режим (саморазвитие)
    return "director"


def run(task: str):
    """
    🚀 Единая точка входа в Megabot
    """

    mode = decide_mode(task)

    print(f"[CentralDecision] task='{task}' → mode={mode}")

    # 🟢 новый слой
    if mode == "engine" and engine_run:
        print("[CentralDecision] → Engine selected")
        return engine_run(task)

    # 🔴 старый слой
    if director_run:
        print("[CentralDecision] → Director selected")
        return director_run(task)

    raise Exception("❌ No execution layer available")
