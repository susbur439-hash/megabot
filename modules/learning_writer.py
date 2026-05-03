import json
import os

MEM_FILE = "internet_memory_v2.json"


# =========================
# 📦 LOAD
# =========================
def load_memory():
    if not os.path.exists(MEM_FILE):
        return []

    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# =========================
# 💾 SAVE
# =========================
def save_memory(memory):
    try:
        with open(MEM_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except:
        pass


# =========================
# ⚙️ WEIGHTS ENGINE (FIXED)
# =========================
def update_weights(memory):
    weights = {}

    for item in memory:
        patterns = item.get("patterns", {})
        score = item.get("score", 50)

        delta = (score - 50) / 10  # нормализация

        for k in patterns:
            if isinstance(k, str):
                weights[k] = weights.get(k, 0) + delta

    return weights


# =========================
# 🧠 LEARN CORE (V3 FIXED)
# =========================
def learn(data):

    data.setdefault("log", [])

    evaluation = data.get("evaluation", {})
    score = evaluation.get("score", 50)

    decision = data.get("decision")
    module = data.get("module")

    if not decision:
        return data

    memory = load_memory()

    # =========================
    # 🧠 CONTEXTUAL PATTERNS (FIX)
    # =========================
    patterns = {}

    patterns[f"decision:{decision}"] = 1

    if module:
        patterns[f"module:{module}"] = 1

    patterns[f"score_range:{'high' if score>=70 else 'mid' if score>=50 else 'low'}"] = 1

    if data.get("task"):
        patterns["task_present"] = 1

    if data.get("create_count", 0) > 2:
        patterns["loop_risk"] = 1

    # =========================
    # 💾 MEMORY ENTRY (FIXED STRUCTURE)
    # =========================
    memory.append({
        "patterns": patterns,
        "score": score,
        "decision": decision,
        "module": module
    })

    # ограничение памяти
    memory = memory[-2000:]

    save_memory(memory)

    # =========================
    # ⚙️ WEIGHTS
    # =========================
    weights = update_weights(memory)

    data["internet_weights"] = weights

    # =========================
    # 🔥 EXTRA SIGNALS (IMPORTANT)
    # =========================
    data["snapshot_bias"] = {
        "create": weights.get("decision:create_module", 0),
        "run": weights.get("decision:run_module", 0),
        "fail": weights.get("score_range:low", 0)
    }

    # =========================
    # 🧾 LOG
    # =========================
    data["log"].append(
        f"🧠 LEARN V3 | score={score} | decision={decision} | module={module}"
    )

    return data
