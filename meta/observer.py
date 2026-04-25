import os
import json
import re

ROOT = "."
RUNTIME_FILE = "runtime_log.json"


# =========================
# 📦 LOAD RUNTIME (НОВОЕ)
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
# 📁 SCAN FILES
# =========================
def scan_files():
    structure = {}

    for root, dirs, files in os.walk(ROOT):
        if ".git" in root:
            continue
        structure[root] = files

    return structure


# =========================
# 🔗 BUILD IMPORT GRAPH
# =========================
def build_import_map(structure):
    imports_map = {}

    for path, files in structure.items():
        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(path, file)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                imports = set()

                imports += set(re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE))
                imports += set(re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE))

                imports_map[full_path] = list(imports)

            except:
                continue

    return imports_map


# =========================
# 🧠 RUNTIME ANALYSIS (ГЛАВНОЕ ДОБАВЛЕНИЕ)
# =========================
def analyze_runtime(calls):
    module_stats = {}
    edges = set()

    for c in calls:
        mod = c.get("module", "unknown")
        module_stats[mod] = module_stats.get(mod, 0) + 1

        # цепочка вызовов (если есть предыдущий модуль)
        if "prev_module" in c:
            edges.add((c["prev_module"], mod))

    hot = sorted(module_stats.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "module_stats": module_stats,
        "hot": hot,
        "edges": list(edges)
    }


# =========================
# 🧟 DEAD MODULES
# =========================
def detect_dead_modules(structure, runtime):
    used = set([c.get("module") for c in runtime])

    dead = []

    for path, files in structure.items():
        for f in files:
            if f.endswith(".py"):
                name = f.replace(".py", "")
                if name not in used and f != "main.py":
                    dead.append(os.path.join(path, f))

    return dead


# =========================
# 🧠 MAIN OBSERVER
# =========================
def run(data=None):
    print("👁 OBSERVER v5 START")

    structure = scan_files()
    runtime = load_runtime()
    imports_map = build_import_map(structure)

    runtime_analysis = analyze_runtime(runtime)
    dead_modules = detect_dead_modules(structure, runtime)

    # =========================
    # 📊 STATS
    # =========================
    stats = {
        "modules": sum(len(v) for v in structure.values()),
        "edges": len(runtime_analysis["edges"]),
        "hot": len(runtime_analysis["hot"]),
        "dead": len(dead_modules)
    }

    # =========================
    # 🧠 HEALTH SCORE
    # =========================
    health = 100
    health -= stats["dead"] * 0.1
    health -= (100 - min(stats["hot"], 20))

    health = max(0, int(health))

    print(f"📊 modules={stats['modules']} edges={stats['edges']}")
    print(f"🔥 hot={stats['hot']} 💀 dead={stats['dead']}")
    print(f"🧠 HEALTH: {health}/100")

    # =========================
    # 🔥 TOP MODULES
    # =========================
    print("\n=== HOT MODULES ===")
    for m, c in runtime_analysis["hot"][:10]:
        print(f"🔥 {m}: {c}")

    # =========================
    # 💀 DEAD MODULES
    # =========================
    print("\n=== DEAD MODULES ===")
    for d in dead_modules[:10]:
        print("💀", d)

    # =========================
    # 🔗 EDGES (FLOW)
    # =========================
    print("\n=== EXECUTION FLOW ===")
    for e in runtime_analysis["edges"][:10]:
        print(f"{e[0]} → {e[1]}")

    print("\n=== END OBSERVER ===")

    return {
        "system_map": {
            "health": health,
            "hot": runtime_analysis["hot"],
            "dead": dead_modules,
            "edges": runtime_analysis["edges"]
        }
    }
