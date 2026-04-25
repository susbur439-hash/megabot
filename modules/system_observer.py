import os
import re
import json


def run(data):
    print("👁 OBSERVER v5 CORE START")

    root = "."
    skip_dirs = {"__pycache__", ".git", "venv", "env"}

    # =========================
    # 📦 LOAD RUNTIME
    # =========================
    runtime_calls = []
    try:
        with open("runtime_log.json", "r", encoding="utf-8") as f:
            runtime_calls = json.load(f).get("calls", [])
    except:
        runtime_calls = []

    # =========================
    # 🧠 RUNTIME MAP
    # =========================
    runtime_used = set()
    runtime_edges = set()

    for c in runtime_calls:
        mod = c.get("module")
        if mod:
            runtime_used.add(mod)

        if c.get("prev_module") and mod:
            runtime_edges.add((c["prev_module"], mod))

    # =========================
    # 📊 STORAGE
    # =========================
    nodes = {}
    modules = []
    imports_map = {}
    static_edges = set()

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

            modules.append(rel)

            try:
                with open(full, "r", encoding="utf-8") as file:
                    content = file.read()
            except:
                continue

            imports = set()
            imports.update(re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE))
            imports.update(re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE))

            cleaned = {i.split(".")[0] for i in imports}
            imports_map[rel] = cleaned

            nodes[rel] = {
                "has_run": "def run(" in content,
                "is_entry": f in ["main.py", "app.py", "bot_start.py"],
                "is_core": any(x in rel for x in ["core", "engine", "control", "system"]),
                "size": len(content)
            }

    module_set = set(modules)

    # =========================
    # 🔗 STATIC GRAPH (CLEAN MATCH)
    # =========================
    for mod, imports in imports_map.items():
        mod_name = os.path.splitext(os.path.basename(mod))[0]

        for imp in imports:
            for target in module_set:
                target_name = os.path.splitext(os.path.basename(target))[0]

                if imp == target_name:
                    static_edges.add((mod, target))

    # =========================
    # 🧠 ACTIVITY SCORE
    # =========================
    hot, cold, dead = [], [], []

    for mod in modules:
        node = nodes.get(mod, {})

        static_usage = any(mod == e[1] for e in static_edges)
        runtime_usage = mod in runtime_used
        runtime_flow = any(mod == e[1] for e in runtime_edges)

        score = 0

        if static_usage:
            score += 40

        if runtime_usage:
            score += 40

        if runtime_flow:
            score += 20

        if node.get("has_run"):
            score += 15

        if node.get("is_core"):
            score += 10

        if node.get("is_entry"):
            score += 20

        if score >= 80:
            hot.append(mod)
        elif score >= 40:
            cold.append(mod)
        else:
            dead.append(mod)

    # =========================
    # 💀 DEAD ANALYSIS
    # =========================
    suggestions = []

    for mod in dead:
        if mod in ["main.py", "app.py", "bot_start.py"]:
            continue

        suggestions.append({
            "module": mod,
            "problem": "module is isolated (no runtime + no graph usage)",
            "fix": "connect into execution flow or remove"
        })

    # =========================
    # 🔗 FULL FLOW GRAPH
    # =========================
    full_edges = list(static_edges.union(runtime_edges))

    # =========================
    # 📊 HEALTH SCORE
    # =========================
    total = len(modules) or 1

    health = int(
        (len(hot) * 100 + len(cold) * 50) / total
    )

    if health >= 75:
        status = "healthy"
    elif health >= 40:
        status = "unstable"
    else:
        status = "critical"

    # =========================
    # 📤 OUTPUT
    # =========================
    report = {
        "modules": total,
        "hot": hot,
        "cold": cold,
        "dead": dead,
        "edges": list(full_edges),
        "runtime_edges": list(runtime_edges),
        "static_edges": list(static_edges),
        "health": health,
        "status": status,
        "suggestions": suggestions
    }

    data["observer_v5"] = report

    print(f"📊 modules={total} edges={len(full_edges)}")
    print(f"🔥 hot={len(hot)} ⚪ cold={len(cold)} 💀 dead={len(dead)}")
    print(f"🧠 HEALTH: {health}/100 → {status}")

    print("\n=== TOP SUGGESTIONS ===")
    for s in suggestions[:10]:
        print("🛠", s)

    print("\n=== END OBSERVER v5 CORE ===")

    return data
