# =========================================================
# 🧠 MEGABOT RUNTIME GRAPH BUILDER v10 (IMPROVED LOOP FIXED)
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
REPORT_FILE = "builder_report.json"

MAX_CYCLES = 1

# =========================================================
# 🧠 CORE MODULES ONLY
# =========================================================

CORE_MODULES = {
    "director",
    "central_decision",
    "execution",
    "engine",
    "observer",
    "control_panel",
    "learning",
    "evaluation",
    "planner",
    "memory",
    "decision",
    "task_interpreter",
    "analysis",
    "router",
    "module_router",
    "control_bus"
}

# =========================================================
# 🎯 SAFE RUNTIME PATTERNS
# =========================================================

RUNTIME_PATTERNS = {
    "director_run": "director",
    "engine_run": "engine"
}

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
        "history": [],
        "last_graph_hash": None,
        "drift": 0
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
# 📄 REPORT
# =========================================================

def save_report(actions, isolated, hubs):

    issues = []
    suggestions = []

    for i in (isolated or []):
        issues.append(f"{i} is isolated")
        suggestions.append(f"connect {i} to core graph")

    for h in (hubs or []):
        suggestions.append(f"optimize {h}")

    report = {
        "issues": issues,
        "suggestions": suggestions,
        "actions": actions or []
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

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

        if ".git" in root or "__pycache__" in root:
            continue

        for f in file_list:

            if not f.endswith(".py"):
                continue

            path = os.path.join(root, f)
            files.append(path)

            if os.path.basename(root) == MODULES_DIR:

                name = f.replace(".py", "")

                if name in CORE_MODULES:
                    modules.append(name)

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

                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)

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
# 🔗 BUILD GRAPH (IMPROVED)
# =========================================================

def build_runtime_graph(files, modules):

    graph = {m: set() for m in modules}
    reverse = {m: set() for m in modules}
    weights = {m: 0 for m in modules}

    for file in files:

        current_module = os.path.basename(file).replace(".py", "")

        if current_module not in graph:
            continue

        code = read_file(file)
        calls = extract_runtime_calls(code)

        for call in calls:

            for target in modules:

                if target == current_module:
                    continue

                linked = (
                    target == call
                    or call.endswith("." + target)
                    or (call in RUNTIME_PATTERNS and RUNTIME_PATTERNS[call] == target)
                )

                if linked:
                    graph[current_module].add(target)
                    reverse[target].add(current_module)
                    weights[current_module] = weights.get(current_module, 0) + 1

    return graph, reverse, weights

# =========================================================
# 🧠 BRAIN
# =========================================================

def find_brain(graph, reverse):

    if not graph:
        return None

    best = None
    best_score = -1

    for node in graph:

        score = len(graph[node]) * 2 + len(reverse[node]) * 3

        if node == "director":
            score += 15
        elif node == "central_decision":
            score += 12
        elif node == "control_panel":
            score += 10
        elif node == "engine":
            score += 8

        if score > best_score:
            best_score = score
            best = node

    return best

# =========================================================
# 🧠 HUBS
# =========================================================

def compute_hubs(graph, reverse, weights):

    hubs = []

    for node in graph:

        score = (
            len(graph[node]) * 2 +
            len(reverse[node]) * 2 +
            weights.get(node, 0)
        )

        if score >= 6:
            hubs.append(node)

    return hubs

# =========================================================
# 🧠 ISOLATED (FIXED)
# =========================================================

def compute_isolated(graph, reverse):

    return [
        node for node in graph
        if len(graph[node]) == 0 and len(reverse[node]) == 0
    ]

# =========================================================
# 🧠 DECISION
# =========================================================

def decide(hubs, isolated):

    actions = []

    for node in (isolated or []):
        actions.append({
            "type": "connect",
            "target": node,
            "reason": "core isolation"
        })

    for node in (hubs or []):
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
# 🧠 CYCLE (FIXED LOOP INTELLIGENCE)
# =========================================================

def build_cycle():

    memory = load_memory()
    files, modules = scan()

    log("\n==============================")
    log("🧠 MEGABOT RUNTIME BUILDER v10 FIXED")
    log("==============================")

    log(f"FILES: {len(files)}")
    log(f"CORE MODULES: {len(modules)}")

    graph, reverse, weights = build_runtime_graph(files, modules)

    brain = find_brain(graph, reverse)

    hubs = compute_hubs(graph, reverse, weights)
    isolated = compute_isolated(graph, reverse)

    actions = decide(hubs, isolated)

    save_report(actions, isolated, hubs)

    # =========================
    # 🧠 DRIFT DETECTION
    # =========================

    prev = memory.get("runtime_graph", {})
    drift = 0

    if prev:
        drift = abs(len(graph) - len(prev))

    memory["drift"] = drift

    memory["runtime_graph"] = {k: list(v) for k, v in graph.items()}
    memory["reverse_graph"] = {k: list(v) for k, v in reverse.items()}
    memory["weights"] = weights

    memory["brain_node"] = brain
    memory["hubs"] = hubs
    memory["isolated"] = isolated
    memory["actions"] = actions

    log("\n🧠 BRAIN STATE")
    log(f"BRAIN NODE: {brain}")
    log(f"HUBS: {len(hubs)}")
    log(f"ISOLATED: {len(isolated)}")
    log(f"DRIFT: {drift}")

    log("\n⚙ ACTIONS")

    for action in actions[:25]:
        log(f"[ACTION] {action['type']} -> {action['target']}")

    errors = validate(files)

    memory["cycles"] += 1

    memory["history"].append({
        "cycle": memory["cycles"],
        "brain": brain,
        "hubs": len(hubs),
        "isolated": len(isolated),
        "actions": len(actions),
        "errors": errors,
        "drift": drift
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