import os
import re
import json


def run(data):
    print("👁 OBSERVER v4 FIXED START")

    root = "."
    skip_dirs = {"__pycache__", ".git", "venv", "env"}

    # =========================
    # 📦 LOAD RUNTIME (НОВОЕ)
    # =========================
    runtime_calls = []
    try:
        with open("runtime_log.json", "r", encoding="utf-8") as f:
            runtime_calls = json.load(f).get("calls", [])
    except:
        runtime_calls = []

    runtime_used = set(
        c.get("module") for c in runtime_calls if c.get("module")
    )

    report = {
        "nodes": {},
        "edges": [],
        "modules": [],
        "hot": [],
        "cold": [],
        "dead": [],
        "warnings": [],
        "critical": [],
        "suggestions": [],
        "health_score": 0,
        "health_status": "unknown"
    }

    imports_map = {}

    # =========================
    # 📁 SCAN
    # =========================
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for f in files:
            if not f.endswith(".py"):
                continue

            full = os.path.join(r, f)
            rel = os.path.relpath(full, root)

            report["modules"].append(rel)

            try:
                with open(full, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception as e:
                report["critical"].append({"file": rel, "error": str(e)})
                continue

            imports = set()
            imports.update(re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE))
            imports.update(re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE))

            cleaned = {i.split(".")[0] for i in imports}
            imports_map[rel] = list(cleaned)

            report["nodes"][rel] = {
                "has_run": "def run(" in content,
                "is_core": "engine" in rel or "core" in rel,
                "size": len(content)
            }

    module_set = set(report["modules"])

    # =========================
    # 🔗 EDGES (SAFE MATCH)
    # =========================
    for mod, imports in imports_map.items():
        for imp in imports:
            for target in module_set:
                if imp in target:
                    report["edges"].append((mod, target))

    # =========================
    # 🧠 CLASSIFICATION (FIXED)
    # =========================
    for mod, node in report["nodes"].items():

        static_usage = any(mod in e[1] for e in report["edges"])
        runtime_usage = mod in runtime_used

        score = 0

        if static_usage or runtime_usage:
            score += 60
        else:
            score -= 30

        if node["has_run"]:
            score += 20

        if node["is_core"]:
            score += 10

        if runtime_usage:
            score += 20

        if score >= 70:
            report["hot"].append(mod)
        elif score >= 30:
            report["cold"].append(mod)
        else:
            report["dead"].append(mod)

    # =========================
    # 💀 DEAD (FIXED LOGIC)
    # =========================
    for mod in report["dead"]:
        report["suggestions"].append({
            "module": mod,
            "problem": "low or no usage (static + runtime)",
            "fix": "connect to runtime flow or remove"
        })

    # =========================
    # 📊 HEALTH
    # =========================
    total = len(report["modules"]) or 1

    score = int(
        (len(report["hot"]) * 100 + len(report["cold"]) * 50) / total
    )

    report["health_score"] = score

    if score >= 70:
        report["health_status"] = "healthy"
    elif score >= 40:
        report["health_status"] = "unstable"
    else:
        report["health_status"] = "critical"

    # =========================
    # 📤 OUTPUT
    # =========================
    data["observer_v4"] = report

    print(f"📊 modules={total} edges={len(report['edges'])}")
    print(f"🔥 hot={len(report['hot'])} ⚪ cold={len(report['cold'])} 💀 dead={len(report['dead'])}")
    print(f"🧠 HEALTH: {score}/100 → {report['health_status']}")

    print("\n=== TOP SUGGESTIONS ===")
    for s in report["suggestions"][:10]:
        print("🛠", s)

    print("\n=== END OBSERVER v4 FIXED ===")

    return data
