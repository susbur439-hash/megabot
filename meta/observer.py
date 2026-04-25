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

            except Exception as e:
                imports_map[full_path] = []

    return imports_map


# =========================
# 🧠 RUNTIME ANALYSIS
# =========================
def analyze_runtime(calls):
    module_stats = {}
    edges = set()

    for c in calls:
        mod = c.get("module", "unknown")
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
# 🧟 DEAD MODULES
# =========================
def detect_dead_modules(structure, runtime):
    used = set([c.get("module") for c in runtime if c.get("module")])

    dead = []

    for path, files in structure.items():
        for f in files:
            if not f.endswith(".py"):
                continue

            name = f.replace(".py", "")

            if name not in used and f != "main.py":
                dead.append(os.path.join(path, f))

    return dead


# =========================
# 🚨 SYSTEM ANALYSIS (NEW)
# =========================
def detect_system_issues(structure, imports_map):
    issues = []
    broken = []
    errors = []

    all_files = {
        os.path.basename(f.replace(".py", "")): f
        for path, files in structure.items()
        for f in files if f.endswith(".py")
    }

    for module, imports in imports_map.items():
        for imp in imports:
            if imp in ["os", "sys", "json", "re", "math", "time"]:
                continue

            if imp not in all_files:
                broken.append({
                    "module": module,
                    "missing": imp
                })

    # простая проверка битых файлов
    for path, files in structure.items():
        for f in files:
            if f.endswith(".py"):
                full = os.path.join(path, f)
                try:
                    with open(full, "r", encoding="utf-8") as x:
                        x.read()
                except Exception as e:
                    errors.append({
                        "file": full,
                        "error": str(e)
                    })

    return issues, broken, errors


# =========================
# 🧠 MAIN OBSERVER v6
# =========================
def run(data=None):
    print("👁 OBSERVER v6 START")

    structure = scan_files()
    runtime = load_runtime()
    imports_map = build_import_map(structure)

    runtime_analysis = analyze_runtime(runtime)
    dead_modules = detect_dead_modules(structure, runtime)

    issues, broken, errors = detect_system_issues(structure, imports_map)

    # =========================
    # 📊 STATS
    # =========================
    stats = {
        "modules": sum(len(v) for v in structure.values()),
        "edges": len(runtime_analysis["edges"]),
        "hot": len(runtime_analysis["hot"]),
        "dead": len(dead_modules),
        "issues": len(issues),
        "broken": len(broken),
        "errors": len(errors)
    }

    # =========================
    # 🧠 HEALTH SCORE
    # =========================
    health = 100
    health -= stats["dead"] * 0.05
    health -= stats["issues"] * 2
    health -= stats["broken"] * 3
    health -= stats["errors"] * 5

    health = max(0, int(health))

    print(f"📊 modules={stats['modules']} edges={stats['edges']}")
    print(f"🔥 hot={stats['hot']} 💀 dead={stats['dead']}")
    print(f"🧠 HEALTH: {health}/100")

    # =========================
    # 🔥 HOT
    # =========================
    print("\n=== HOT MODULES ===")
    for m, c in runtime_analysis["hot"]:
        print(f"🔥 {m}: {c}")

    # =========================
    # 💀 DEAD
    # =========================
    print("\n=== DEAD MODULES ===")
    for d in dead_modules[:10]:
        print("💀", d)

    # =========================
    # 🚨 ISSUES
    # =========================
    print("\n=== ISSUES ===")
    for i in issues[:10]:
        print("⚠️", i)

    print("\n=== BROKEN IMPORTS ===")
    for b in broken[:10]:
        print("🔗", b)

    print("\n=== ERRORS ===")
    for e in errors[:10]:
        print("❌", e)

    print("\n=== END OBSERVER ===")

    return {
        "system_map": {
            "health": health,
            "hot": runtime_analysis["hot"],
            "dead": dead_modules,
            "edges": runtime_analysis["edges"],
            "architecture_issues": issues,
            "broken_links": broken,
            "errors": errors
        }
    }
