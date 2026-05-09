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
# 🧠 DATA CONTRACT v1 NORMALIZER
# =========================
def normalize_task(task):
    """
    ЕДИНЫЙ КОНТРАКТ ДЛЯ ВСЕГО MEGABOT
    """

    # -------------------------
    # string input
    # -------------------------
    if isinstance(task, str):
        text = task

    # -------------------------
    # dict input
    # -------------------------
    elif isinstance(task, dict):

        text = (
            task.get("task")
            or task.get("input")
            or json.dumps(task, ensure_ascii=False)
        )

    # -------------------------
    # fallback
    # -------------------------
    else:
        text = str(task)

    return {
        "raw": task,
        "text": text,
        "lower": text.lower(),
        "original": task
    }


# =========================
# 🧠 ANALYSIS LAYER
# =========================
def analyze(task) -> dict:

    t = normalize_task(task)

    return {
        **t,
        "is_system": any(k in t["lower"] for k in [
            "system", "list", "modules", "router",
            "status", "scan", "repo", "health", "debug", "logs"
        ]),
        "needs_external": any(k in t["lower"] for k in [
            "search", "internet", "learn", "external"
        ])
    }


# =========================
# 🧠 STRATEGY DECISION
# =========================
def decide_strategy(analysis: dict) -> str:

    if analysis["needs_external"] and gateway:
        return "external"

    if analysis["is_system"]:
        return "engine"

    return "director"


# =========================
# ⚙️ EXECUTION LAYER
# =========================
def execute(strategy: str, analysis: dict):

    print(f"[CentralDecision] strategy={strategy}")

    # 🌐 external
    if strategy == "external" and gateway:
        print("[CentralDecision] → External Gateway")
        return gateway.call("search", analysis["text"])

    # ⚙️ engine
    if strategy == "engine" and engine_run:
        print("[CentralDecision] → Engine selected")
        return engine_run(analysis)

    # 🧠 director
    if director_run:
        print("[CentralDecision] → Director selected")
        return director_run(analysis)

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

    return execute(strategy, analysis)
