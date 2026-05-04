import os
import json

from modules.task_core import extract_task, normalize_task
from modules.run import run_task
from modules.decision import decide
from modules.evaluation import run as evaluate
from modules.learning_writer import learn
from modules.snapshot_learning_core import inject_snapshot_learning

# 🧠 CONTROL BUS
from modules.control_bus import inject, emit, feedback


MEMORY_FILE = "memory.json"


def load_memory_experience():
    try:
        if not os.path.exists(MEMORY_FILE):
            return []

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)

        if not isinstance(memory, list) or not memory:
            return []

        last = memory[-1]

        return last.get("experience", [])

    except:
        return []


def save_memory_experience(data):
    try:
        memory = []

        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                memory = json.load(f)

        if not isinstance(memory, list):
            memory = []

        memory.append({
            "experience": data.get("experience", [])
        })

        memory = memory[-50:]

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)

    except Exception as e:
        data.setdefault("log", []).append(f"❌ MEMORY SAVE ERROR: {e}")


def run(data):
    # 🛡️ защита входа
    if not isinstance(data, dict):
        data = {}

    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("evaluation", {})
    data.setdefault("create_count", 0)

    try:
        data["log"].append("🎬 DIRECTOR START")

        # =========================
        # 💾 LOAD MEMORY (КЛЮЧЕВОЙ ФИКС)
        # =========================
        if not data.get("experience"):
            data["experience"] = load_memory_experience()

        # =========================
        # 🧠 CONTROL BUS INJECT
        # =========================
        data = inject(data)

        # =========================
        # 🧠 TASK PREPROCESS
        # =========================
        try:
            task = extract_task(data)
        except Exception:
            task = data.get("task", "")

        try:
            task = normalize_task(task)
        except Exception:
            pass

        data["task"] = task

        # =========================
        # 🧠 DECISION
        # =========================
        decide(data)

        action = data.get("decision")
        module = data.get("module")

        data["log"].append(f"🧠 DECISION: {action} | module: {module}")

        # =========================
        # 📡 CONTROL BUS EVENT (decision)
        # =========================
        emit({
            "action": action,
            "module": module,
            "phase": "decision"
        })

        # =========================
        # 🧠 SNAPSHOT LEARNING
        # =========================
        try:
            data = inject_snapshot_learning(data)
        except Exception as e:
            data["log"].append(f"❌ SNAPSHOT ERROR: {e}")

        # =========================
        # 🧨 ANTI-LOOP
        # =========================
        if action == "create_module":
            data["create_count"] += 1

            if data["create_count"] >= 3 and data.get("experience"):
                best = max(data["experience"], key=lambda x: x.get("score", 0))

                data["module"] = best.get("module")
                data["decision"] = "run_module"

                data["log"].append("🧠 ANTI-LOOP → forced run_module")
        else:
            data["create_count"] = 0

        # =========================
        # 🚀 EXECUTION
        # =========================
        result = run_task(data)

        if isinstance(result, dict):
            for k, v in result.items():
                if k == "log" and isinstance(v, list):
                    data["log"].extend(v)
                else:
                    data[k] = v
        else:
            data["result"] = result

        # =========================
        # 📡 CONTROL BUS EVENT (execution)
        # =========================
        emit({
            "action": action,
            "module": module,
            "result": data.get("status", "unknown"),
            "phase": "execution"
        })

        # =========================
        # 📊 EVALUATION
        # =========================
        eval_result = evaluate(data)

        if not isinstance(eval_result, dict):
            eval_result = {"score": 0, "delta": -50, "result": "error"}

        data["evaluation"] = eval_result
        score = eval_result.get("score", 0)

        # =========================
        # 🧠 LEARNING
        # =========================
        try:
            data = learn(data)
        except Exception as e:
            data["log"].append(f"❌ LEARNING ERROR: {e}")

        # =========================
        # 💾 EXPERIENCE
        # =========================
        if module:
            if (
                not data["experience"]
                or data["experience"][-1].get("module") != module
            ):
                data["experience"].append({
                    "module": module,
                    "score": score
                })

        # =========================
        # 💾 SAVE MEMORY (КЛЮЧЕВОЙ ФИКС)
        # =========================
        save_memory_experience(data)

        # =========================
        # 📊 CONTROL BUS FEEDBACK
        # =========================
        feedback()

        # =========================
        # 📊 LOG
        # =========================
        data["log"].append(f"📊 SCORE: {score}")
        data["log"].append("🎬 DIRECTOR END")

        return data

    except Exception as e:
        import traceback

        data["status"] = "error"
        data["error"] = str(e)
        data["trace"] = traceback.format_exc()

        data["log"].append(f"❌ DIRECTOR ERROR: {e}")

        return data
