# =========================================================
# 🧠 MEGABOT RUNTIME GRAPH BUILDER v9
# 🧠 REAL EXECUTION FLOW ANALYZER
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
# 🎯 RUNTIME CALL PATTERNS
# =========================================================

RUNTIME_PATTERNS = [
    "run",
    "execute",
    "director_run",
    "engine_run",
    "gateway.call",
    "route",
    "dispatch",
    "forward",
    "process",
    "handle",
    "decide",
    "analyze"
]

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
        "runtime_graph": {},
        "reverse_graph": {},
        "weights": {},
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

    files = []
    modules = []

    for root, _, file_list in os.walk(ROOT_DIR):

        if ".git" in root:
            continue

        if "__pycache__" in root:
            continue

        for f in file_list:

            if not f.endswith(".py"):
                continue

            path = os.path.join(root, f)

            files.append(path)

            if os.path.basename(root) == MODULES_DIR:
                modules.append(f.replace(".py", ""))

    return files, modules

# =========================================================
# 🧠 AST CALL EXTRACTOR
# =========================================================

def extract_runtime_calls(code):

    calls = []

    try:

        tree = ast.parse(code)

        for node in ast.walk(tree):

            if isinstance(node, ast.Call):

                # -------------------------
                # simple call
                # -------------------------
                if isinstance(node.func, ast.Name):

                    calls.append(node.func.id)

                # -------------------------
                # attribute call
                # -------------------------
                elif isinstance(node.func, ast.Attribute):

                    parts = []

                    current = node.func

                    while isinstance(current, ast.Attribute):

                        parts.append(current.attr)
                        current = current.value

                    if isinstance(current, ast.Name):
                        parts.append(current.id)

                    parts.reverse()

                    calls.append(".".join(parts))

    except:
        pass

    return calls

# =========================================================
# 🔗 BUILD RUNTIME GRAPH
# =========================================================

def build_runtime_graph(files, modules):

    graph = {}
    reverse = {}
    weights = {}

    for m in modules:

        graph[m] = set()
        reverse[m] = set()
        weights[m] = 0

    for file in files:

        current_module = os.path.basename(file).replace(".py", "")

        if current_module not in graph:
            continue

        code = read_file(file)

        calls = extract_runtime_calls(code)

        # -------------------------
        # runtime module linking
        # -------------------------
        for call in calls:

            for target in modules:

                # -------------------------
                # runtime call hit
                # -------------------------
                if (
                    target in call
                    or call in RUNTIME_PATTERNS
                ):

                    if target != current_module:

                        graph[current_module].add(target)

                        reverse[target].add(current_module)

                        weights[current_module] += 1

    return graph, reverse, weights

# =========================================================
# 🧠 FIND BRAIN NODE
# =========================================================

def find_brain(graph, reverse):

    best = None
    best_score = -1

    for node in graph:

        score = (
            len(graph[node]) * 2 +
            len(reverse[node]) * 3
        )

        if "director" in node:
            score += 10

        if "central" in node:
            score += 8

        if "control" in node:
            score += 5

        if score > best_score:
            best_score = score
            best = node

    return best

# =========================================================
# 🧠 HUB DETECTOR
# =========================================================

def compute_hubs(graph, reverse, weights):

    hubs = []

    for node in graph:

        score = (
            len(graph[node]) * 2 +
            len(reverse[node]) * 2 +
            weights[node]
        )

        if score >= 5:
            hubs.append(node)

    return hubs

# =========================================================
# 🧠 ISOLATED DETECTOR
# =========================================================

def compute_isolated(graph, reverse):

    isolated = []

    for node in graph:

        if (
            len(graph[node]) == 0 and
            len(reverse[node]) == 0
        ):
            isolated.append(node)

    return isolated

# =========================================================
# 🧠 DECISION LAYER
# =========================================================

def decide(hubs, isolated):

    actions = []

    for node in isolated:

        actions.append({
            "type": "connect",
            "target": node,
            "reason": "runtime isolation"
        })

    for node in hubs:

        actions.append({
            "type": "optimize",
            "target": node,
            "reason": "high runtime traffic"
        })

    return actions

# =========================================================
# 🧪 VALIDATION
# =========================================================

def validate(files):

    errors = 0

    for file in files:

        try:

            code = read_file(file)

            compile(code, file, "exec")

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
    log("🧠 MEGABOT RUNTIME BUILDER v9")
    log("==============================")

    log(f"FILES: {len(files)}")
    log(f"MODULES: {len(modules)}")

    # =====================================================
    # 🔗 RUNTIME GRAPH
    # =====================================================

    graph, reverse, weights = build_runtime_graph(
        files,
        modules
    )

    # =====================================================
    # 🧠 ANALYSIS
    # =====================================================

    brain = find_brain(graph, reverse)

    hubs = compute_hubs(
        graph,
        reverse,
        weights
    )

    isolated = compute_isolated(
        graph,
        reverse
    )

    actions = decide(
        hubs,
        isolated
    )

    # =====================================================
    # 💾 MEMORY
    # =====================================================

    memory["runtime_graph"] = {
        k: list(v)
        for k, v in graph.items()
    }

    memory["reverse_graph"] = {
        k: list(v)
        for k, v in reverse.items()
    }

    memory["weights"] = weights

    memory["brain_node"] = brain
    memory["hubs"] = hubs
    memory["isolated"] = isolated
    memory["actions"] = actions

    # =====================================================
    # 📋 LOGGING
    # =====================================================

    log("\n🧠 BRAIN STATE")
    log(f"BRAIN NODE: {brain}")
    log(f"HUBS: {len(hubs)}")
    log(f"ISOLATED: {len(isolated)}")

    log("\n⚙ ACTIONS")

    for action in actions[:25]:

        log(
            f"[ACTION] "
            f"{action['type']} -> "
            f"{action['target']}"
        )

    # =====================================================
    # 🧪 VALIDATION
    # =====================================================

    errors = validate(files)

    memory["cycles"] += 1

    memory["history"].append({
        "cycle": memory["cycles"],
        "brain": brain,
        "hubs": len(hubs),
        "isolated": len(isolated),
        "actions": len(actions),
        "errors": errors
    })

    save_memory(memory)

    # =====================================================
    # 📊 DONE
    # =====================================================

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
