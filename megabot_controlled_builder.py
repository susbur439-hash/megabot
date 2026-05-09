# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v8.3 FIXED CORE++
# 🧠 SINGLE GRAPH + ARCH BRAIN SYNC + CLOSED LOOP FIX
# =========================================================

import os
import json
import traceback
import ast

# =========================================================
# ⚙ CONFIG
# =========================================================

ROOT_DIR = "."
MODULES_DIR = "modules"

MEMORY_FILE = "builder_memory.json"

MAX_CYCLES = 1

# =========================================================
# 📋 LOG
# =========================================================

def log(msg):
    print(msg)

# =========================================================
# 💾 MEMORY
# =========================================================

def load_memory():
    default = {
        "cycles": 0,
        "connections": {},
        "reverse_connections": {},
        "weights": {},
        "roles": {},
        "brain_node": None,
        "hubs": [],
        "isolated": [],
        "actions": [],
        "history": []
    }

    if not os.path.exists(MEMORY_FILE):
        return default

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default.items():
            data.setdefault(k, v)
        return data
    except:
        return default


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

# =========================================================
# 📖 FILE
# =========================================================

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# =========================================================
# 🔍 SCAN
# =========================================================

def scan():
    files, modules = [], []

    for root, _, file_list in os.walk(ROOT_DIR):

        if ".git" in root or "__pycache__" in root:
            continue

        for f in file_list:
            if not f.endswith(".py"):
                continue

            path = os.path.join(root, f)
            files.append(path)

            if os.path.basename(root) == MODULES_DIR:
                modules.append(f)

    return files, modules

# =========================================================
# 🧠 AST IMPORTS
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

    return imports

# =========================================================
# 🔗 SINGLE GRAPH (FIXED CORE)
# =========================================================

def build_graph(files, modules):

    module_names = [m.replace(".py", "") for m in modules]

    graph = {m: set() for m in module_names}
    reverse = {m: set() for m in module_names}
    weights = {m: 0 for m in module_names}

    for file in files:

        name = os.path.basename(file).replace(".py", "")
        code = read_file(file)
        imports = extract_imports(code)

        if name not in graph:
            continue

        for imp in imports:
            if imp in graph:
                graph[name].add(imp)
                reverse[imp].add(name)
                weights[name] += 1

    return graph, reverse, weights

# =========================================================
# 🧠 HUB DETECTION
# =========================================================

def compute_hubs(graph, reverse, weights):

    hubs = []

    for node in graph:

        score = len(graph[node]) + len(reverse[node]) + weights[node]

        if score >= 2:
            hubs.append(node)

    return hubs

# =========================================================
# 🧠 ROLE ENGINE (LOCAL, NOT EXTERNAL)
# =========================================================

def compute_roles(graph):

    roles = {}

    for node in graph:

        if len(graph[node]) == 0 and len(reverse_connections.get(node, [])) == 0:
            roles[node] = "isolated"
        elif len(graph[node]) >= 3:
            roles[node] = "hub"
        else:
            roles[node] = "module"

    return roles

# =========================================================
# 🧠 DECISION LAYER
# =========================================================

def decide(graph, reverse, hubs, isolated):

    actions = []

    for n in isolated:
        actions.append({"type": "connect", "target": n})

    for n in hubs:
        actions.append({"type": "optimize", "target": n})

    return actions

# =========================================================
# 🧠 EXECUTION (SAFE ONLY LOGIC)
# =========================================================

def execute(actions):

    for a in actions:
        log(f"[ACTION] {a['type']} -> {a['target']}")

# =========================================================
# 🧪 VALIDATION
# =========================================================

def validate(modules):

    errors = 0

    for m in modules:
        try:
            path = os.path.join(MODULES_DIR, m)
            code = read_file(path)
            compile(code, path, "exec")
            ast.parse(code)
        except:
            errors += 1

    return errors

# =========================================================
# 🧠 MAIN LOOP
# =========================================================

def build_cycle():

    memory = load_memory()

    files, modules = scan()

    log("\n==============================")
    log("🧠 MEGABOT v8.3 FIXED CORE++")
    log("==============================")

    log(f"FILES: {len(files)} | MODULES: {len(modules)}")

    # =========================
    # GRAPH
    # =========================

    graph, reverse, weights = build_graph(files, modules)

    # =========================
    # BRAIN
    # =========================

    hubs = compute_hubs(graph, reverse, weights)

    isolated = [
        n for n in graph
        if len(graph[n]) == 0 and len(reverse[n]) == 0
    ]

    roles = {
        n: ("hub" if n in hubs else "isolated" if n in isolated else "module")
        for n in graph
    }

    # =========================
    # DECISION
    # =========================

    actions = decide(graph, reverse, hubs, isolated)

    execute(actions)

    # =========================
    # MEMORY SYNC
    # =========================

    memory["connections"] = {k: list(v) for k, v in graph.items()}
    memory["reverse_connections"] = {k: list(v) for k, v in reverse.items()}
    memory["weights"] = weights

    memory["roles"] = roles
    memory["hubs"] = hubs
    memory["isolated"] = isolated
    memory["actions"] = actions

    log("\n🧠 BRAIN STATE")
    log(f"HUBS: {len(hubs)}")
    log(f"ISOLATED: {len(isolated)}")

    errors = validate(modules)

    memory["cycles"] += 1

    memory["history"].append({
        "cycle": memory["cycles"],
        "errors": errors,
        "hubs": len(hubs),
        "isolated": len(isolated),
        "actions": len(actions)
    })

    save_memory(memory)

    log("\n==============================")
    log("📊 DONE")
    log("==============================")

    log(f"cycles={memory['cycles']}")
    log(f"errors={errors}")

# =========================================================
# ▶ RUN
# =========================================================

if __name__ == "__main__":

    try:
        for _ in range(MAX_CYCLES):
            build_cycle()

    except Exception as e:
        log(f"FATAL: {e}")
        log(traceback.format_exc())
