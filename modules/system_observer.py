import os
import re


def run(data):
    print("👁 OBSERVER v4 SCAN START")

    root = "."
    skip_dirs = {"__pycache__", ".git", "venv", "env"}

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
    usage_map = {}

    # =========================
    # 📁 SCAN PROJECT
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
                report["critical"].append({
                    "type": "read_error",
                    "file": rel,
                    "error": str(e)
                })
                continue

            imports = set()
            imports.update(re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE))
            imports.update(re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE))

            cleaned = {i.split(".")[0] for i in imports}
            imports_map[rel] = list(cleaned)

            report["nodes"][rel] = {
                "has_run": "def run(" in content,
                "size": len(content),
                "complexity": content.count("\n"),
                "is_core": "engine" in rel or "core" in rel,
                "is_router": "router" in content.lower()
            }

            usage_map[rel] = 0

    # =========================
    # 🔗 BUILD GRAPH
    # =========================
    module_set = set(report["modules"])

    for mod, imports in imports_map.items():
        for imp in imports:
            for target in module_set:
                if target.endswith(f"{imp}.py"):
                    report["edges"].append((mod, target))
                    usage_map[target] = usage_map.get(target, 0) + 1

    # =========================
    # 🧠 CLASSIFICATION
    # =========================
    for mod, node in report["nodes"].items():
        usage = usage_map.get(mod, 0)

        score = 0

        # usage weight
        if usage > 0:
            score += 50
        else:
            score -= 20

        # logic presence
        if node["has_run"]:
            score += 25

        # complexity
        if node["complexity"] > 50:
            score += 10

        # core system boost
        if node["is_core"]:
            score += 10

        # router boost
        if node["is_router"]:
            score += 15

        # classification
        if score >= 70:
            report["hot"].append(mod)
        elif score >= 30:
            report["cold"].append(mod)
        else:
            report["dead"].append(mod)

    # =========================
    # 🧠 SELF-HEAL SUGGESTIONS
    # =========================
    for mod in report["dead"]:
        report["suggestions"].append({
            "module": mod,
            "problem": "module is unused or isolated",
            "fix": "connect module to router or remove if obsolete"
        })

    for mod in report["cold"]:
        report["suggestions"].append({
            "module": mod,
            "problem": "low activity module",
            "fix": "increase usage or integrate into engine flow"
        })

    # =========================
    # 📊 HEALTH SCORE
    # =========================
    total = len(report["modules"]) or 1

    score = int(
        (len(report["hot"]) * 100 +
         len(report["cold"]) * 40) / total
    )

    report["health_score"] = score

    if score >= 75:
        report["health_status"] = "healthy"
    elif score >= 40:
        report["health_status"] = "unstable"
    else:
        report["health_status"] = "critical"

    # =========================
    # 📤 RETURN
    # =========================
    data["observer_v4"] = report

    print(f"📊 modules={total} edges={len(report['edges'])}")
    print(f"🔥 hot={len(report['hot'])} ⚪ cold={len(report['cold'])} 💀 dead={len(report['dead'])}")
    print(f"🧠 HEALTH: {score}/100 → {report['health_status']}")

    print("\n=== TOP SUGGESTIONS ===")
    for s in report["suggestions"][:10]:
        print("🛠", s)

    print("\n=== END OBSERVER v4 ===")

    data.setdefault("log", []).append(
        f"observer_v4: score={score} status={report['health_status']}"
    )

    return data
