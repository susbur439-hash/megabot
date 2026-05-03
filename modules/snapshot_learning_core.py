import json
import os
import re

SNAPSHOT_FILE = "full_system_snapshot.txt"
MEMORY_FILE = "memory.json"


# =========================
# 📦 LOAD SNAPSHOT
# =========================
def load_snapshot_text():
    try:
        if not os.path.exists(SNAPSHOT_FILE):
            return ""
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


# =========================
# 📦 LOAD MEMORY (SAFE FIX)
# =========================
def load_memory():
    try:
        if not os.path.exists(MEMORY_FILE):
            return []

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 🔥 FIX: memory must ALWAYS be list
        if isinstance(data, list):
            return data

        return []

    except:
        return []


# =========================
# 🧠 PATTERN EXTRACTION (SAFE)
# =========================
def extract_patterns(text):
    patterns = {}

    if not isinstance(text, str):
        return patterns

    # modules
    modules = re.findall(r"module_[a-zA-Z0-9_]+", text)
    for m in modules:
        patterns[f"module:{m}"] = patterns.get(f"module:{m}", 0) + 1

    # decisions
    decisions = re.findall(r"decision:\s*([a-zA-Z_]+)", text)
    for d in decisions:
        patterns[f"decision:{d}"] = patterns.get(f"decision:{d}", 0) + 1

    # scores
    scores = re.findall(r"score[:= ]+(\d+)", text)
    for s in scores:
        try:
            s = int(s)
        except:
            continue

        if s >= 80:
            patterns["success_high"] = patterns.get("success_high", 0) + 1
        elif s >= 60:
            patterns["success_mid"] = patterns.get("success_mid", 0) + 1
        else:
            patterns["success_low"] = patterns.get("success_low", 0) + 1

    # system states
    if "create_module" in text:
        patterns["mode:create"] = patterns.get("mode:create", 0) + 1

    if "run_module" in text:
        patterns["mode:run"] = patterns.get("mode:run", 0) + 1

    return patterns


# =========================
# 🧠 BUILD WEIGHTS (SAFE)
# =========================
def build_weights(patterns, memory):
    weights = {}

    if not isinstance(patterns, dict):
        patterns = {}

    if not isinstance(memory, list):
        memory = []

    # current snapshot
    for k, v in patterns.items():
        weights[k] = weights.get(k, 0) + (v or 0)

    # historical memory boost
    for item in memory:
        if not isinstance(item, dict):
            continue

        mem_patterns = item.get("patterns", {})

        if not isinstance(mem_patterns, dict):
            continue

        for k, v in mem_patterns.items():
            weights[k] = weights.get(k, 0) + (v or 0) * 0.5

    return weights


# =========================
# 🚀 CORE ENGINE
# =========================
def snapshot_learning_core():
    text = load_snapshot_text()
    memory = load_memory()

    patterns = extract_patterns(text)
    weights = build_weights(patterns, memory)

    # safe append
    memory.append({
        "patterns": patterns,
        "weights": weights
    })

    # limit memory
    memory = memory[-50:]

    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except:
        pass

    return weights


# =========================
# 🔌 INJECT INTO DATA (FIXED)
# =========================
def inject_snapshot_learning(data):
    if not isinstance(data, dict):
        data = {}

    data.setdefault("log", [])

    weights = snapshot_learning_core()

    if not isinstance(weights, dict):
        weights = {}

    data["snapshot_weights"] = weights

    # safe bias extraction
    data["snapshot_bias"] = {
        "create": weights.get("mode:create", 0),
        "run": weights.get("mode:run", 0),
        "success": (
            weights.get("success_mid", 0) +
            weights.get("success_high", 0)
        )
    }

    data["log"].append(
        f"🧠 SNAPSHOT LEARNED | create={data['snapshot_bias']['create']} | run={data['snapshot_bias']['run']}"
    )

    return data
