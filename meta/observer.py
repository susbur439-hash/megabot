import os
import json
import re

ROOT = "."
RUNTIME_FILE = "runtime_log.json"

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
# 📁 SCAN FILES
# =========================
def scan_files():
    structure = {}

    for root, dirs, files in os.walk(ROOT):
        if ".git" in root:
            continue
        if "__pycache__" in root:
            continue

        structure[root] = files

    return structure


# =========================
# 🔗 IMPORT MAP
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

                imports.update(re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE))
                imports.update(re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE))

                imports_map[full_path] = list(imports)

            except:
                imports_map[full_path] = []

    return imports_map


# =========================
# 🧠 RUNTIME ANALYSIS
# =========================
def analyze_runtime(calls):
    module_stats = {}
    edges = set()

    for c in calls:
        mod = c.get("module")
        if not mod:
            continue

        module_stats[mod] = module_stats.get(mod, 0) + 1

        if "prev_module" in c:
            edges.add((c["prev_module"], mod))

    hot = sorted(module_stats.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "module_stats": module_stats,
        "hot": hot,
        "edges": list(edges)
    }


# =========================
# 🧠 REAL LIVE MODULE CHECK
# =========================
def get_live_modules(runtime, imports_map):
    live = set()

    # runtime usage
    for c in runtime:
        if c.get("module"):
            live.add(c["module"])

    # imports usage
    for module, imports in imports_map.items():
        for imp in imports:
            live.add(imp)

    # always alive core
    live.update(["main", "control", "router"])

    return live


# =========================
# 🧟 DEAD MODULES (FIXED)
# =========================
def detect_dead_modules(structure, live_modules):
    dead = []

    for path, files in structure.items():
        for f in files:
            if not f.endswith(".py"):
                continue

            name = f.replace(".py", "")

            if name not in live_modules:
                # не убиваем core
                if name in ["main", "control", "__init__"]:
                    continue

                dead.append(os.path.join(path, f))

    return dead


# =========================
# 🚨 SYSTEM ISSUES
# =========================
def detect_system_issues(structure, imports_map):
    broken = []
    errors = []

    all_modules = {
        f.replace(".py", "")
        for path, files in structure.items()
        for f in files if f.endswith(".py")
    }

    for module, imports in imports_map.items():
        for imp in imports:

            # skip stdlib
            if imp in ["os", "sys", "json", "re", "math", "time"]:
                continue

            if imp not in all_modules:
                broken.append({
                    "module": module,
                    "missing": imp
                })

    return broken, errors


# =========================
# 🧠 MAIN OBSERVER v7
# =========================
def run(data=None):
    print("👁 OBSERVER v7 START")

    structure = scan_files()
    runtime = load_runtime()
    imports_map = build_import_map(structure)

    runtime_analysis = analyze_runtime(runtime)

    live_modules = get_live_modules(runtime, imports_map)
    dead_modules = detect_dead_modules(structure, live_modules)

    broken, errors = detect_system_issues(structure, imports_map)

    # =========================
    # 📊 STATS
    # =========================
    stats = {
        "modules": sum(len(v) for v in structure.values()),
        "edges": len(runtime_analysis["edges"]),
        "hot": len(runtime_analysis["hot"]),
        "dead": len(dead_modules),
        "broken": len(broken),
        "errors": len(errors)
    }

    # =========================
    # 🧠 HEALTH SCORE
    # =========================
    health = 100
    health -= stats["dead"] * 0.1
    health -= stats["broken"] * 2
    health -= stats["errors"] * 5

    health = max(0, int(health))

    print(f"📊 modules={stats['modules']} edges={stats['edges']}")
    print(f"🔥 hot={stats['hot']} 💀 dead={stats['dead']}")
    print(f"🧠 HEALTH: {health}/100")

    print("\n=== HOT MODULES ===")
    for m, c in runtime_analysis["hot"]:
        print(f"🔥 {m}: {c}")

    print("\n=== DEAD MODULES ===")
    for d in dead_modules[:15]:
        print("💀", d)

    print("\n=== BROKEN IMPORTS ===")
    for b in broken[:15]:
        print("🔗", b)

    print("\n=== END OBSERVER ===")

    return {
        "system_map": {
            "health": health,
            "hot": runtime_analysis["hot"],
            "dead": dead_modules,
            "edges": runtime_analysis["edges"],
            "broken_links": broken,
            "errors": errors
        }
    }
