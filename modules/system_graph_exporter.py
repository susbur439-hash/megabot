import os
import json

def build_graph(root="."):
    graph = {
        "files": [],
        "imports": {},
        "calls": {}
    }

    for path, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".py"):
                continue

            full = os.path.join(path, f)

            try:
                with open(full, "r", encoding="utf-8") as file:
                    code = file.read()
            except:
                continue

            graph["files"].append(full)

            # imports
            imports = []
            for line in code.split("\n"):
                if line.strip().startswith("from ") or line.strip().startswith("import "):
                    imports.append(line.strip())

            graph["imports"][full] = imports

            # crude call detection
            calls = []
            for line in code.split("\n"):
                if "(" in line and ")" in line and "def " not in line:
                    calls.append(line.strip()[:120])

            graph["calls"][full] = calls[:30]

    return graph


def export_system_graph():
    graph = build_graph()

    with open("system_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    print("📦 SYSTEM GRAPH SAVED")

    return graph
