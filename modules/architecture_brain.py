# =========================================================
# 🧠 MEGABOT ARCHITECTURE BRAIN v1
# 🔗 Role + Connection Analyzer (for Bolduen / Connection Manager)
# =========================================================

import os
import ast

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
# 🔍 EXTRACT IMPORTS (AST SAFE)
# =========================================================

def extract_imports(code):
    imports = set()

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split(".")[0])

            if isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

    except:
        pass

    return imports


# =========================================================
# 🧠 ROLE DETECTOR
# =========================================================

def detect_role(name, imports):

    # core brain nodes
    if name in ["director", "central_decision"]:
        return "brain"

    if "execution" in name:
        return "execution"

    if "observer" in name:
        return "observer"

    if "control" in name or "gate" in name or "bus" in name:
        return "control"

    if len(imports) == 0:
        return "isolated"

    return "module"


# =========================================================
# 🔗 BUILD ARCHITECTURE GRAPH
# =========================================================

def build_architecture_graph(files):

    graph = {}
    roles = {}

    for path in files:

        if not path.endswith(".py"):
            continue

        name = os.path.basename(path).replace(".py", "")

        code = read_file(path)
        imports = extract_imports(code)

        graph[name] = list(imports)
        roles[name] = detect_role(name, imports)

    return graph, roles


# =========================================================
# 🧠 FIND SYSTEM CORE (BRAIN NODE)
# =========================================================

def find_brain_node(roles, graph):

    # priority search
    for node, role in roles.items():
        if role == "brain":
            return node

    # fallback: most connected
    max_links = -1
    best = None

    for node, edges in graph.items():
        if len(edges) > max_links:
            max_links = len(edges)
            best = node

    return best


# =========================================================
# 🔗 BUILD CONNECTION WEIGHTS
# =========================================================

def build_weights(graph):

    weights = {}

    for node, edges in graph.items():

        weights[node] = {}

        for e in edges:
            weights[node][e] = weights[node].get(e, 0) + 1

    return weights


# =========================================================
# 🧠 MAIN API (USED BY BOLDUEN)
# =========================================================

def analyze(files):

    graph, roles = build_architecture_graph(files)

    brain = find_brain_node(roles, graph)

    weights = build_weights(graph)

    isolated = [n for n, r in roles.items() if r == "isolated"]

    hubs = [
        n for n, edges in graph.items()
        if len(edges) >= 5
    ]

    return {
        "graph": graph,
        "roles": roles,
        "brain": brain,
        "weights": weights,
        "hubs": hubs,
        "isolated": isolated
    }
