import os
import json
import re

ROOT = "."

skip_dirs = {"__pycache__", ".git", "venv", "env"}

std_libs = {
    "os", "sys", "json", "re", "math", "random",
    "time", "datetime", "collections", "itertools",
    "subprocess", "threading", "asyncio", "logging",
    "importlib", "traceback"
}


# =========================
# 📦 SCAN FILES
# =========================
def scan_files():
    modules = []
    structure = {}

    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        structure[root] = files

        for f in files:
            if f.endswith(".py"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, ROOT)
                modules.append(rel)

    return modules, structure


# =========================
# 🔗 IMPORT ANALYSIS
# =========================
def analyze_imports(modules):
    imports_map = {}

    for module in modules:
        try:
            with open(module, "r", encoding="utf-8") as f:
                content = f.read()

            imports = set()

            matches = re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE)
            matches += re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE)

            for m in matches:
                base = m.split(".")[0]
                if base:
                    imports.add(base)

            imports_map[module] = list(imports)

        except:
            imports_map[module] = []

    return imports_map


# =========================
# 🔗 CONNECTION GRAPH
# =========================
def build_connections(modules, imports_map):
    connections = {}

    for m in modules:
        connections[m] = {
            "imports": imports_map.get(m, []),
            "used_by": []
        }

    for module, imports in imports_map.items():
        for imp in imports:
            if imp in std_libs:
                continue

            for other in modules:
                if imp in other:
                    connections[other]["used_by"].append(module)

    return connections


# =========================
# 🧟 DEAD + CORE
# =========================
def classify_modules(connections):
    dead = []
    core = []

    for m, conn in connections.items():
        if not conn["used_by"] and "main.py" not in m:
            dead.append(m)

        if len(conn["used_by"]) > 2:
            core.append(m)

    return dead, core


# =========================
# 📊 STRUCTURE CHECK
# =========================
def check_structure(structure):
    warnings = []
    issues = []

    found_paths = set(structure.keys())

    expected_dirs = ["modules", "meta", "megabot_core"]

    for d in expected_dirs:
        if not any(d in path for path in found_paths):
            warnings.append(f"missing layer: {d}")

    if not any("main.py" in files for files in structure.values()):
        issues.append("missing main.py")

    return issues, warnings


# =========================
# 🧠 SCORE
# =========================
def system_score(issues, warnings, dead_count):
    score = 100
    score -= len(issues) * 25
    score -= len(warnings) * 5
    score -= int(dead_count * 0.05)

    return max(0, min(100, score))


# =========================
# 🚀 MAIN OBSERVER
# =========================
def run(data):
    print("👁 OBSERVER v6 START")

    modules, structure = scan_files()
    imports_map = analyze_imports(modules)
    connections = build_connections(modules, imports_map)
    dead, core = classify_modules(connections)

    issues, warnings = check_structure(structure)

    score = system_score(issues, warnings, len(dead))

    # =========================
    # 💾 SYSTEM MAP
    # =========================
    system_map = {
        "modules": modules,
        "connections": connections,
        "dead_modules": dead,
        "core_modules": core,
        "issues": issues,
        "warnings": warnings,
        "stats": {
            "total": len(modules),
            "dead": len(dead),
            "core": len(core),
            "score": score
        }
    }

    try:
        with open("system_map.json", "w", encoding="utf-8") as f:
            json.dump(system_map, f, ensure_ascii=False, indent=2)
        print("💾 system_map.json saved")
    except Exception as e:
        print("❌ save error:", e)

    # =========================
    # 📊 OUTPUT
    # =========================
    print(f"📊 modules={len(modules)}")
    print(f"💀 dead={len(dead)}")
    print(f"🧠 core={len(core)}")
    print(f"🏁 score={score}/100")

    if issues:
        print("❌ issues:", issues[:3])

    if warnings:
        print("⚠️ warnings:", warnings[:3])

    print("✅ OBSERVER v6 DONE")

    data["system_map"] = system_map
    return data
