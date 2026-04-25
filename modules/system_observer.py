import os
import re
import json

ROOT = "."
RUNTIME_FILE = "runtime_log.json"


# =========================
# 🧠 NORMALIZATION (КЛЮЧЕВОЕ)
# =========================
def norm(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


# =========================
# 📦 LOAD RUNTIME
# =========================
def load_runtime():
    if not os.path.exists(RUNTIME_FILE):
        return []

    try:
        with open(RUNTIME_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("calls", [])
    except:
        return []


# =========================
# 📁 SCAN
# =========================
def scan():
    structure = {}

    for root, dirs, files in os.walk(ROOT):
        if ".git" in root or "__pycache__" in root:
            continue
        structure[root] = files

    return structure


# =========================
# 🧠 INDEX
# =========================
def index(structure):
    modules = {}
    imports_map = {}

    for path, files in structure.items():
        for f in files:
            if not f.endswith(".py"):
                continue

            full = os.path.join(path, f)

            try:
                content = open(full, "r", encoding="utf-8").read()
            except:
                continue

            name = norm(f)

            modules[name] = {
                "path": full,
                "has_run": "def run(" in content,
                "is_entry": f in ["main.py", "app.py", "bot_start.py"],
                "size": len(content)
            }

            imports = set()
            imports.update(re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE))
            imports.update(re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE))

            imports_map[name] = {i.split(".")[0] for i in imports}

    return modules, imports_map


# =========================
# 🔥 RUNTIME TRUTH
# =========================
def runtime_truth(calls):
    used = {}
    edges = set()

    for c in calls:
        m = c.get("module")
        p = c.get("prev_module")

        if m:
            nm = norm(m)
            used[nm] = used.get(nm, 0) + 1

        if m and p:
            edges.add((norm(p), norm(m)))

    return used, edges


# =========================
# 🧠 CLASSIFIER (TRUTH-BASED)
# =========================
def classify(modules, imports_map, runtime_used, runtime_edges):
    hot, cold, dead = [], [], []

    for name, meta in modules.items():

        runtime_score = runtime_used.get(name, 0) > 0
        static_score = any(name in imports_map.get(name2, set()) for name2 in imports_map)
        flow_score = any(name == b for a, b in runtime_edges)

        score = 0

        # 🔥 MAIN TRUTH = RUNTIME
        if runtime_score:
            score += 70

        if flow_score:
            score += 20

        if static_score:
            score += 10

        if meta["has_run"]:
            score += 10

        if meta["is_entry"]:
            score += 15

        if score >= 80:
            hot.append(name)
        elif score >= 40:
            cold.append(name)
        else:
            dead.append(name)

    return hot, cold, dead


# =========================
# 🧠 MAIN OBSERVER v6 TRUTH
# =========================
def run(data=None):
    print("👁 OBSERVER v6 TRUTH START")

    structure = scan()
    modules, imports_map = index(structure)

    runtime = load_runtime()
    runtime_used, runtime_edges = runtime_truth(runtime)

    hot, cold, dead = classify(modules, imports_map, runtime_used, runtime_edges)

    total = len(modules) or 1

    health = int(
        (len(hot) * 100 + len(cold) * 50) / total
    )

    health = max(0, min(100, health))

    # =========================
    # 📤 OUTPUT
    # =========================
    print(f"📊 modules={total}")
    print(f"🔥 hot={len(hot)} ⚪ cold={len(cold)} 💀 dead={len(dead)}")
    print(f"🧠 HEALTH: {health}/100")

    print("\n=== HOT ===")
    for m in hot[:10]:
        print("🔥", m)

    print("\n=== DEAD ===")
    for m in dead[:10]:
        print("💀", m)

    return {
        "system_map": {
            "health": health,
            "hot": hot,
            "cold": cold,
            "dead": dead,
            "runtime_used": runtime_used,
            "runtime_edges": list(runtime_edges)
        }
    }
