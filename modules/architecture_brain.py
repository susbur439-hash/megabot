# =========================================================
# 🧠 MEGABOT ARCHITECTURE BRAIN v2 (ENHANCED CORE)
# 🔗 True Dependency Graph + Role System + Core Detection
# =========================================================

import os
import ast
from collections import defaultdict

MODULES_DIR = "modules"


# =========================================================
# 📖 READ FILE
# =========================================================

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


# =========================================================
# 🔍 IMPORT EXTRACTOR (AST + FALLBACK)
# =========================================================

def extract_imports(code):
    imports = set()

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

    except:
        pass

    # fallback (если AST пропустил)
    for line in code.splitlines():
        line = line.strip()

        if line.startswith("import "):
            imports.add(line.split(" ")[1].split(".")[0])

        if line.startswith("from "):
            parts = line.split(" ")
            if len(parts) > 1:
                imports.add(parts[1].split(".")[0])

    return imports


# =========================================================
# 🧠 ROLE SYSTEM (ENHANCED)
# =========================================================

def detect_role(name, imports):

    if name in ["director", "central_decision", "engine", "megabot_controlled_builder"]:
        return "brain"

    if "execution" in name:
        return "execution"

    if "observer" in name:
        return "observer"

    if "control" in name or "gate" in name or "bus" in name:
        return "control"

    if "builder" in name:
        return "builder"

    if len(imports) == 0:
        return "isolated"

    return "module"


# =========================================================
# 🔗 BUILD DIRECTED GRAPH (REAL DEPENDENCIES)
# =========================================================

def build_architecture_graph(files):

    graph = defaultdict(set)
    reverse_graph = defaultdict(set)
    weights = defaultdict(lambda: defaultdict(int))

    modules = set()

    # collect module names
    for path in files:
        if path.endswith(".py"):
            name = os.path.basename(path).replace(".py", "")
            modules.add(name)

    for path in files:

        if not path.endswith(".py"):
            continue

        name = os.path.basename(path).replace(".py", "")

        code = read_file(path)
        imports = extract_imports(code)

        for imp in imports:

            if imp in modules and imp != name:

                # directed edge
                graph[name].add(imp)
                reverse_graph[imp].add(name)

                # weight = frequency of reference
                weights[name][imp] += 1

    return graph, reverse_graph, weights


# =========================================================
# 🧠 CORE BRAIN DETECTION (REAL METRICS)
# =========================================================

def find_brain_node(roles, graph, reverse_graph):

    scores = {}

    for node in graph.keys():

        out_deg = len(graph[node])
        in_deg = len(reverse_graph[node])

        role_bonus = 5 if roles.get(node) == "brain" else 0

        # core score formula
        score = (in_deg * 2) + out_deg + role_bonus

        scores[node] = score

    if not scores:
        return None

    return max(scores, key=scores.get)


# =========================================================
# 🔗 HUB DETECTION (IMPROVED)
# =========================================================

def detect_hubs(graph, reverse_graph):

    hubs = []

    for node in graph.keys():

        total_links = len(graph[node]) + len(reverse_graph[node])

        if total_links >= 10:
            hubs.append(node)

    return hubs


# =========================================================
# 🧠 ISOLATION DETECTION
# =========================================================

def detect_isolated(graph, reverse_graph):

    isolated = []

    for node in graph.keys():

        if len(graph[node]) == 0 and len(reverse_graph[node]) == 0:
            isolated.append(node)

    return isolated


# =========================================================
# 📊 GRAPH METRICS
# =========================================================

def compute_density(graph):

    nodes = len(graph)
    edges = sum(len(v) for v in graph.values())

    if nodes == 0:
        return 0

    return round(edges / nodes, 3)


# =========================================================
# 🧠 MAIN API (BOLDUEN CORE INTERFACE)
# =========================================================

def analyze(files):

    graph, reverse_graph, weights = build_architecture_graph(files)

    roles = {}
    for node in graph.keys():
        roles[node] = detect_role(node, graph[node])

    brain = find_brain_node(roles, graph, reverse_graph)

    hubs = detect_hubs(graph, reverse_graph)
    isolated = detect_isolated(graph, reverse_graph)

    density = compute_density(graph)

    return {
        "graph": {k: list(v) for k, v in graph.items()},
        "reverse_graph": {k: list(v) for k, v in reverse_graph.items()},
        "weights": {k: dict(v) for k, v in weights.items()},
        "roles": roles,
        "brain": brain,
        "hubs": hubs,
        "isolated": isolated,
        "density": density
    }
