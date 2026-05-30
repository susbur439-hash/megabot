import json
from core.system_state import system_state

# existing modules
from modules.task_core import extract_task
from modules.decision import decide
from modules.control_bus import inject, emit
from modules.control_gate import detect, filter_decision
from modules.evaluation import run as evaluate
from modules.learning_writer import learn
from modules.run import run_task


# =========================
# 🧠 UNIFIED CORE LOOP
# =========================
def run(task):

    log = []

    # =========================
    # 1. STATE LOAD
    # =========================
    state = system_state.load()
    state = system_state.inject({"task": task})

    log.append("🧠 STATE LOADED")

    # =========================
    # 2. TASK EXTRACTION
    # =========================
    try:
        task_text = extract_task({"task": task})
    except:
        task_text = str(task)

    state["task_text"] = task_text
    log.append(f"📌 TASK: {task_text}")

    # =========================
    # 3. CONTROL BUS INJECT
    # =========================
    state = inject(state)

    # =========================
    # 4. CONTROL GATE (SAFETY)
    # =========================
    detect(state)
    gate = filter_decision(state)

    if not gate.get("allowed", True):
        state["decision"] = gate.get("forced_decision", "run_module")
        log.append("🛑 GATE OVERRIDE")

    # =========================
    # 5. DECISION LAYER
    # =========================
    decide(state)

    decision = state.get("decision")
    module = state.get("module")

    log.append(f"🧠 DECISION: {decision} | {module}")

    # =========================
    # 6. EXECUTION
    # =========================
    result = run_task(state)

    state.update(result)

    log.append("⚙️ EXECUTION DONE")

    # =========================
    # 7. EVALUATION
    # =========================
    try:
        eval_result = evaluate(state)
    except:
        eval_result = {"score": 0}

    state["evaluation"] = eval_result
    score = eval_result.get("score", 0)

    log.append(f"📊 SCORE: {score}")

    # =========================
    # 8. LEARNING
    # =========================
    try:
        state = learn(state)
    except Exception as e:
        log.append(f"❌ LEARN ERROR: {e}")

    # =========================
    # 9. MEMORY UPDATE
    # =========================
    state["experience"].append({
        "module": module,
        "score": score
    })

    state["experience"] = state["experience"][-100:]

    # =========================
    # 10. CONTROL BUS FEEDBACK
    # =========================
    emit({
        "phase": "unified_cycle",
        "decision": decision,
        "module": module,
        "score": score
    })

    # =========================
    # 11. SAVE STATE
    # =========================
    system_state.update("last_result", state)
    system_state.save_memory()

    log.append("💾 STATE SAVED")
    log.append("🔁 CYCLE END")

    state["log"] = log

    return state