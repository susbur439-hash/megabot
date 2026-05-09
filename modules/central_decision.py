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
# 🛡 SAFE NORMALIZATION (FIX v8 CONTRACT ISSUE)
# =========================
def normalize_task(task):
    """
    Приводит вход к безопасному формату:
    - str → string
    - dict → extracts usable text
    """

    if isinstance(task, str):
        return task, task.lower()

    if isinstance(task, dict):
        raw = str(task)

        # пытаемся вытащить полезное поле
        if "task" in task:
            raw = str(task["task"])
        elif "input" in task:
            raw = str(task["input"])

        return raw, raw.lower()

    return str(task), str(task).lower()


# =========================
# 🧠 Анализ задачи
# =========================
def analyze(task) -> dict:

    raw, t = normalize_task(task)

    return {
        "raw": raw,
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

    print(f"[CentralDecision] strategy={strategy} task={task}")

    if strategy == "external" and gateway:
        print("[CentralDecision] → External Gateway")
        return gateway.call("search", str(task))

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
# 🚀 ENTRY POINT (v8 SAFE)
# =========================
def run(task):

    analysis = analyze(task)
    strategy = decide_strategy(analysis)

    return execute(strategy, task)
