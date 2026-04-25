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

# (опционально) внешний источник
try:
    from external_gateway import ExternalGateway
    gateway = ExternalGateway()
except:
    gateway = None


# =========================
# 🧠 Анализ задачи
# =========================
def analyze(task: str) -> dict:
    t = task.lower()

    return {
        "raw": task,
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
def execute(strategy: str, task: str):

    print(f"[CentralDecision] strategy={strategy} task='{task}'")

    # 🌐 внешний источник
    if strategy == "external":
        print("[CentralDecision] → External Gateway")
        return gateway.call("search", task)

    # ⚙️ engine
    if strategy == "engine" and engine_run:
        print("[CentralDecision] → Engine selected")
        return engine_run(task)

    # 🧠 director
    if director_run:
        print("[CentralDecision] → Director selected")
        return director_run(task)

    return {
        "status": "error",
        "message": "No execution layer available"
    }


# =========================
# 🚀 Главная точка входа
# =========================
def run(task: str):

    analysis = analyze(task)
    strategy = decide_strategy(analysis)

    return execute(strategy, task)
