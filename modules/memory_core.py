import json
import os
from collections import defaultdict

MEM_FILE = "megabot_memory_core.json"


# =========================
# 💾 LOAD MEMORY
# =========================
def load_memory():
    if not os.path.exists(MEM_FILE):
        return {
            "modules": {},
            "history": []
        }

    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "modules": {},
            "history": []
        }


# =========================
# 💾 SAVE MEMORY
# =========================
def save_memory(mem):
    try:
        with open(MEM_FILE, "w", encoding="utf-8") as f:
            json.dump(mem, f, ensure_ascii=False, indent=2)
    except:
        pass


# =========================
# 🧠 UPDATE MEMORY
# =========================
def update_memory(data):
    mem = load_memory()

    module = data.get("module")
    score = data.get("evaluation", {}).get("score", 0)
    decision = data.get("decision")

    if module:
        if module not in mem["modules"]:
            mem["modules"][module] = {
                "uses": 0,
                "avg_score": 0,
                "last_score": 0
            }

        m = mem["modules"][module]

        m["uses"] += 1
        m["last_score"] = score

        # 📊 обновление среднего
        m["avg_score"] = (m["avg_score"] * (m["uses"] - 1) + score) / m["uses"]

    mem["history"].append({
        "module": module,
        "score": score,
        "decision": decision
    })

    # ограничение истории
    mem["history"] = mem["history"][-500:]

    save_memory(mem)
    return mem


# =========================
# 🧠 GET BEST MODULE
# =========================
def get_best_module():
    mem = load_memory()
    modules = mem.get("modules", {})

    best = None
    best_score = -999

    for m, stats in modules.items():
        # баланс: средняя оценка + частота
        score = stats["avg_score"] + (stats["uses"] * 0.5)

        if score > best_score:
            best_score = score
            best = m

    return best, best_score


# =========================
# ⚖️ INFLUENCE DECISION
# =========================
def influence_decision(data):
    best_module, best_score = get_best_module()

    data["memory_bias"] = {
        "best_module": best_module,
        "score": best_score
    }

    # 🔥 если есть хороший модуль → уменьшаем create
    if best_module and best_score > 10:
        if data.get("evaluation", {}).get("score", 50) < 80:
            data["suggested_module"] = best_module
            data["suggested_action"] = "run_module"

    return data
