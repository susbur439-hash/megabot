# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v8.3 FIXED CORE++
# 🧠 AST + ARCH BRAIN + REVERSE GRAPH + WEIGHTED SYNC FIXED
# =========================================================

import os
import json
import traceback
import ast

from modules.architecture_brain import analyze

# =========================================================
# ⚙ CONFIG
# =========================================================

ROOT_DIR = "."
MODULES_DIR = "modules"

ARCH_FILE = "architecture.json"
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
# 🔗 GRAPH BUILDER (FIXED NORMALIZATION)
# =========================================================

def build_graph(files, modules):

    graph = {}
    reverse = {}
    weights = {}

    module_names = [m.replace(".py", "") for m in modules]

    for m in module_names:
        graph[m] = set()
        reverse[m] = set()
        weights[m] = 0

    for file in files:

        code = read_file(file)
        imports = extract_imports(code)

        for mod in module_names:

            if mod in imports:

                graph[mod].add(file)
                weights[mod] += 1

                for imp in imports:
                    if imp in reverse:
                        reverse[imp].add(mod)

    return graph, reverse, weights

# =========================================================
# 🧠 ARCH BRAIN SYNC
# =========================================================

def run_arch(files):

    result = analyze(files)

    return {
        "graph": result["graph"],
        "roles": result["roles"],
        "brain": result["brain"],
        "hubs": result["hubs"],
        "isolated": result["isolated"]
    }

# =========================================================
# 🧠 HUB DETECTOR (FIXED SCORE MODEL)
# =========================================================

def compute_hubs(graph, reverse, weights):

    hubs = []

    for node in graph:

        score = (
            len(graph[node]) * 2 +
            len(reverse[node]) * 3 +
            weights[node] * 1
        )

        if score >= 3:
            hubs.append(node)

    return hubs

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
# 🧠 MAIN CYCLE
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
    # ARCH BRAIN
    # =========================

    brain = run_arch(files)

    hubs = compute_hubs(graph, reverse, weights)

    # =========================
    # MEMORY SYNC
    # =========================

    memory["connections"] = {k: list(v) for k, v in graph.items()}
    memory["reverse_connections"] = {k: list(v) for k, v in reverse.items()}
    memory["weights"] = weights

    memory["roles"] = brain["roles"]
    memory["brain_node"] = brain["brain"]
    memory["hubs"] = hubs
    memory["isolated"] = brain["isolated"]

    log("\n🧠 ARCH BRAIN")
    log(f"BRAIN NODE: {brain['brain']}")
    log(f"HUBS: {len(hubs)}")
    log(f"ISOLATED: {len(brain['isolated'])}")

    # =========================
    # VALIDATION
    # =========================

    errors = validate(modules)

    memory["cycles"] += 1

    memory["history"].append({
        "cycle": memory["cycles"],
        "errors": errors,
        "brain": memory["brain_node"],
        "hubs": len(hubs),
        "isolated": len(memory["isolated"])
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
