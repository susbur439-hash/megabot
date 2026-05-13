# modules/system_observer.py

import os
import re
import json

from core.system_state import system_state

ROOT = "."
RUNTIME_FILE = "runtime_log.json"


# =========================
# 🧠 NORMALIZATION
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

            data = json.load(f)

            return data.get("calls", [])

    except Exception:

        return []


# =========================
# 📁 SCAN REPOSITORY
# =========================
def scan():

    structure = {}

    for root, dirs, files in os.walk(ROOT):

        # =========================
        # 🚫 SKIP
        # =========================
        if ".git" in root:
            continue

        if "__pycache__" in root:
            continue

        structure[root] = files

    return structure


# =========================
# 🧠 INDEX FILES
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

                with open(full, "r", encoding="utf-8") as file:
                    content = file.read()

            except Exception:
                continue

            name = norm(f)

            # =========================
            # 🧠 MODULE META
            # =========================
            modules[name] = {
                "path": full,
                "has_run": "def run(" in content,
                "is_entry": f in [
                    "main.py",
                    "app.py",
                    "bot_start.py"
                ],
                "size": len(content)
            }

            # =========================
            # 🔗 IMPORT LINKS
            # =========================
            imports = set()

            imports.update(
                re.findall(
                    r"^\s*import\s+([\w\.]+)",
                    content,
                    re.MULTILINE
                )
            )

            imports.update(
                re.findall(
                    r"^\s*from\s+([\w\.]+)\s+import",
                    content,
                    re.MULTILINE
                )
            )

            imports_map[name] = {
                i.split(".")[0]
                for i in imports
            }

    return modules, imports_map


# =========================
# 🔥 RUNTIME TRUTH
# =========================
def runtime_truth(calls):

    used = {}
    edges = set()

    for c in calls:

        if not isinstance(c, dict):
            continue

        m = c.get("module")
        p = c.get("prev_module")

        if m:

            nm = norm(m)

            used[nm] = used.get(nm, 0) + 1

        if m and p:

            edges.add((
                norm(p),
                norm(m)
            ))

    return used, edges


# =========================
# 🧠 CLASSIFIER
# =========================
def classify(
    modules,
    imports_map,
    runtime_used,
    runtime_edges
):

    hot = []
    cold = []
    dead = []

    for name, meta in modules.items():

        runtime_score = runtime_used.get(name, 0) > 0

        static_score = any(
            name in imports_map.get(name2, set())
            for name2 in imports_map
        )

        flow_score = any(
            name == b
            for a, b in runtime_edges
        )

        score = 0

        # =========================
        # 🔥 RUNTIME PRIORITY
        # =========================
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

        # =========================
        # 🧠 CLASSIFICATION
        # =========================
        if score >= 80:
            hot.append(name)

        elif score >= 40:
            cold.append(name)

        else:
            dead.append(name)

    return hot, cold, dead


# =========================
# 🧠 DETECT MISSING LINKS
# =========================
def detect_missing_links(modules, imports_map):

    missing = []

    for module_name, imports in imports_map.items():

        for imp in imports:

            if imp not in modules:

                missing.append({
                    "module": module_name,
                    "missing_dependency": imp
                })

    return missing


# =========================
# 🧠 UPDATE SYSTEM STATE
# =========================
def update_state(observer_result):

    try:

        state = system_state.load()

        state["observer"] = observer_result

        state["health"] = observer_result.get(
            "health",
            0
        )

        state["hot_modules"] = observer_result.get(
            "hot",
            []
        )

        state["dead_modules"] = observer_result.get(
            "dead",
            []
        )

        system_state.update(
            "observer",
            observer_result
        )

        system_state.save_memory()

    except Exception as e:

        print(f"❌ STATE UPDATE ERROR: {e}")


# =========================
# 🚀 MAIN OBSERVER
# =========================
def run(data=None):

    print("👁 OBSERVER v7 STATE START")

    # =========================
    # 📁 SCAN
    # =========================
    structure = scan()

    # =========================
    # 🧠 INDEX
    # =========================
    modules, imports_map = index(structure)

    # =========================
    # 🔥 RUNTIME
    # =========================
    runtime = load_runtime()

    runtime_used, runtime_edges = runtime_truth(runtime)

    # =========================
    # 🧠 CLASSIFY
    # =========================
    hot, cold, dead = classify(
        modules,
        imports_map,
        runtime_used,
        runtime_edges
    )

    # =========================
    # 🔗 MISSING LINKS
    # =========================
    missing_links = detect_missing_links(
        modules,
        imports_map
    )

    # =========================
    # 📊 HEALTH
    # =========================
    total = len(modules) or 1

    health = int(
        (
            len(hot) * 100 +
            len(cold) * 50
        ) / total
    )

    health = max(0, min(100, health))

    # =========================
    # 📤 RESULT
    # =========================
    result = {
        "health": health,
        "hot": hot,
        "cold": cold,
        "dead": dead,
        "runtime_used": runtime_used,
        "runtime_edges": list(runtime_edges),
        "missing_links": missing_links,
        "total_modules": total
    }

    # =========================
    # 🧠 UPDATE STATE
    # =========================
    update_state(result)

    # =========================
    # 📊 LOGS
    # =========================
    print(f"📊 modules={total}")

    print(
        f"🔥 hot={len(hot)} "
        f"⚪ cold={len(cold)} "
        f"💀 dead={len(dead)}"
    )

    print(f"🧠 HEALTH: {health}/100")

    print(
        f"🔗 missing_links={len(missing_links)}"
    )

    print("\n=== HOT ===")

    for m in hot[:10]:
        print("🔥", m)

    print("\n=== DEAD ===")

    for m in dead[:10]:
        print("💀", m)

    # =========================
    # 📦 RETURN
    # =========================
    return {
        "system_map": result
    }
