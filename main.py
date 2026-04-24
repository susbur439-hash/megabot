import sys
import os

# =========================
# 📦 PATH
# =========================
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# =========================
# 🔌 ENGINE
# =========================
try:
    from core.engine import Engine
    ENGINE_AVAILABLE = True
except Exception as e:
    print("[Engine] not available:", e)
    ENGINE_AVAILABLE = False

# =========================
# 🎯 DIRECTOR (fallback слой)
# =========================
from modules.director import run as director_run


# =========================
# 🔥 DIRECT EXECUTION MODE
# =========================
def run_direct_command(cmd):
    if isinstance(cmd, str) and cmd.endswith(".py") and os.path.exists(cmd):
        print(f"🚀 Direct run: {cmd}")
        os.system(f"python {cmd}")
        return True
    return False


# =========================
# 🧠 ENGINE VALIDATION
# =========================
def engine_can_handle(result):
    if not isinstance(result, dict):
        return False

    if result.get("status") == "ok":
        return True

    return False


# =========================
# 🚀 MAIN
# =========================
if __name__ == "__main__":

    task = "развивай себя"

    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])

    print("🚀 Megabot старт")
    print("🎯 Задача:", task)

    # =========================
    # 🔥 DIRECT MODE
    # =========================
    if run_direct_command(task):
        sys.exit(0)

    engine_result = None

    # =========================
    # 🧠 ENGINE FIRST
    # =========================
    if ENGINE_AVAILABLE:
        print("[Main] Engine try...")

        try:
            engine = Engine()

            command = {
                "module": "system",
                "action": "list",
                "task": task
            }

            engine_result = engine.execute(command)
            print("[Main] Engine result:", engine_result)

        except Exception as e:
            print("[Main] Engine error:", e)
            engine_result = None

    # =========================
    # 🔁 DECISION LAYER
    # =========================
    if engine_can_handle(engine_result):
        print("[Main] Engine handled task → STOP")
    else:
        print("[Main] Fallback → Director")
        director_run(task)
