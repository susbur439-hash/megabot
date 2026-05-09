import json

# =========================
# 🧠 Подключение ядер
# =========================
try:
    from modules.director import run as director_run
except:
    director_run = None

try:
    from modules.engine import run as engine_run
except:
    engine_run = None

try:
    from external_gateway import ExternalGateway
    gateway = ExternalGateway()
except:
    gateway = None


# =========================
# 🧠 SAFE NORMALIZE INPUT
# =========================
def normalize_task(task):
    """
    Всегда приводим вход к строке
    чтобы не падал .lower()
    """

    if task is None:
        return ""

    if isinstance(task, str):
        return task

    if isinstance(task, dict):
        # пробуем извлечь текст
        return (
            task.get("task")
            or task.get("input")
            or json.dumps(task, ensure_ascii=False)
        )

    return str(task)


# =========================
# 🧠 Анализ задачи
# =========================
def analyze(task) -> dict:

    task_str = normalize_task(task)
    t = task_str.lower()

    return {
        "raw": task,
        "normalized": task_str,
        "is_system": any(k in t for k in [
            "system", "list", "modules", "router",
            "status", "scan", "repo", "health", "debug", "logs"
        ]),
        "needs_external": any(k in t for k in [
            "search", "internet", "learn", "external"
        ])
    }


# =========================
# 🧠 Выбор стратегии
# =========================
def decide_strategy(analysis: dict) -> str:

    if analysis["needs_external"] and gateway:
        return "external"

    if analysis["is_system"]:
        return "engine"

    return "director"


# =========================
# ⚙️ Выполнение
# =========================
def execute(strategy: str, task):

    print(f"[CentralDecision] strategy={strategy} task_type={type(task)}")

    if strategy == "external":
        print("[CentralDecision] → External Gateway")
        return gateway.call("search", normalize_task(task))

    if strategy == "engine" and engine_run:
        print("[CentralDecision] → Engine selected")
        return engine_run(task)

    if director_run:
        print("[CentralDecision] → Director selected")
        return director_run(task)

    return {
        "status": "error",
        "message": "No execution layer available"
    }


# =========================
# 🚀 ENTRY POINT
# =========================
def run(task):

    analysis = analyze(task)
    strategy = decide_strategy(analysis)

    return execute(strategy, task)
