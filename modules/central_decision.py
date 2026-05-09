import json

# =========================
# 🧠 SAFE IMPORTS
# =========================
director_run = None
engine_run = None
gateway = None

# -------------------------
# Director
# -------------------------
try:
    from modules.director import run as director_run
    print("[CentralDecision] Director loaded")
except Exception as e:
    print(f"[CentralDecision] Director load failed: {e}")

# -------------------------
# Engine
# -------------------------
try:
    from modules.engine import run as engine_run
    print("[CentralDecision] Engine loaded")
except Exception as e:
    print(f"[CentralDecision] Engine load failed: {e}")

# -------------------------
# External Gateway
# -------------------------
try:
    from external_gateway import ExternalGateway

    gateway = ExternalGateway()

    print("[CentralDecision] External Gateway loaded")

except Exception as e:
    print(f"[CentralDecision] External Gateway failed: {e}")


# =========================
# 🧠 DATA CONTRACT v1 NORMALIZER
# =========================
def normalize_task(task):
    """
    ЕДИНЫЙ КОНТРАКТ ДЛЯ ВСЕГО MEGABOT
    """

    # -------------------------
    # STRING INPUT
    # -------------------------
    if isinstance(task, str):

        text = task.strip()

    # -------------------------
    # DICT INPUT
    # -------------------------
    elif isinstance(task, dict):

        text = (
            task.get("task")
            or task.get("input")
            or task.get("text")
            or json.dumps(task, ensure_ascii=False)
        )

    # -------------------------
    # FALLBACK
    # -------------------------
    else:

        text = str(task)

    # -------------------------
    # SAFETY
    # -------------------------
    if not isinstance(text, str):
        text = str(text)

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

    system_keywords = [
        "system",
        "list",
        "modules",
        "router",
        "status",
        "scan",
        "repo",
        "health",
        "debug",
        "logs"
    ]

    external_keywords = [
        "search",
        "internet",
        "learn",
        "external",
        "google",
        "web"
    ]

    return {
        **t,

        "is_system": any(
            k in t["lower"]
            for k in system_keywords
        ),

        "needs_external": any(
            k in t["lower"]
            for k in external_keywords
        )
    }


# =========================
# 🧠 STRATEGY DECISION
# =========================
def decide_strategy(analysis: dict) -> str:

    # 🌐 External
    if analysis.get("needs_external") and gateway:
        return "external"

    # ⚙️ System / Engine
    if analysis.get("is_system") and engine_run:
        return "engine"

    # 🧠 Default Director
    if director_run:
        return "director"

    # ❌ Nothing available
    return "none"


# =========================
# ⚙️ EXECUTION LAYER
# =========================
def execute(strategy: str, analysis: dict):

    print(f"[CentralDecision] strategy={strategy}")

    # -------------------------
    # 🌐 EXTERNAL
    # -------------------------
    if strategy == "external":

        try:

            print("[CentralDecision] → External Gateway")

            result = gateway.call(
                "search",
                analysis["text"]
            )

            return {
                "status": "success",
                "strategy": strategy,
                "result": result
            }

        except Exception as e:

            return {
                "status": "error",
                "strategy": strategy,
                "message": f"External execution failed: {e}"
            }

    # -------------------------
    # ⚙️ ENGINE
    # -------------------------
    if strategy == "engine":

        try:

            print("[CentralDecision] → Engine selected")

            result = engine_run(analysis)

            return {
                "status": "success",
                "strategy": strategy,
                "result": result
            }

        except Exception as e:

            return {
                "status": "error",
                "strategy": strategy,
                "message": f"Engine execution failed: {e}"
            }

    # -------------------------
    # 🧠 DIRECTOR
    # -------------------------
    if strategy == "director":

        try:

            print("[CentralDecision] → Director selected")

            result = director_run(analysis)

            return {
                "status": "success",
                "strategy": strategy,
                "result": result
            }

        except Exception as e:

            return {
                "status": "error",
                "strategy": strategy,
                "message": f"Director execution failed: {e}"
            }

    # -------------------------
    # ❌ FALLBACK
    # -------------------------
    return {
        "status": "error",
        "strategy": strategy,
        "message": "No execution layer available"
    }


# =========================
# 🚀 ENTRY POINT
# =========================
def run(task):

    try:

        analysis = analyze(task)

        print(f"[CentralDecision] task={analysis['text']}")

        strategy = decide_strategy(analysis)

        return execute(strategy, analysis)

    except Exception as e:

        return {
            "status": "fatal_error",
            "message": str(e)
        }


# =========================
# 🧪 LOCAL TEST
# =========================
if __name__ == "__main__":

    test_task = {
        "task": "scan repo status"
    }

    result = run(test_task)

    print("\n=== RESULT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
