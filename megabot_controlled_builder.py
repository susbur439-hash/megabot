import os
import json
import traceback
import ast
import hashlib

# =========================================================
# ⚙ CONFIG
# =========================================================

ROOT_DIR = "."
MODULES_DIR = "modules"

MEMORY_FILE = "builder_memory.json"
REPORT_FILE = "builder_report.json"

MAX_CYCLES = 1

# =========================================================
# 🧠 CORE MODULES
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
# 🎯 PATTERNS
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
# 🔐 GRAPH HASH (NEW)
# =========================================================

def hash_graph(graph):
    try:
        flat = {k: sorted(list(v)) for k, v in graph.items()}
        raw = json.dumps(flat, sort_keys=True).encode()
        return hashlib.md5(raw).hexdigest()
    except:
        return None

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
        "graph_hash": None,
        "drift": 0,
        "learning_score": {}
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

    report = {
        "issues": [f"{i} isolated" for i in (isolated or [])],
        "suggestions": (
            [f"connect {i}" for i in (isolated or [])] +
            [f"optimize {h}" for h in (hubs or [])]
        ),
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
# 🧠 AST
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
                    cur = node.func

                    while isinstance(cur, ast.Attribute):
                        parts.append(cur.attr)
                        cur = cur.value

                    if isinstance(cur, ast.Name):
                        parts.append(cur.id)

                    parts.reverse()
                    calls.append(".".join(parts))

    except:
        pass

    return calls

# =========================================================
# 🔗 GRAPH BUILD
# =========================================================

def build_runtime_graph(files, modules):

    graph = {m: set() for m in modules}
    reverse = {m: set() for m in modules}
    weights = {m: 0 for m in modules}

    for file in files:

        current = os.path.basename(file).replace(".py", "")

        if current not in graph:
            continue

        code = read_file(file)
        calls = extract_runtime_calls(code)

        for call in calls:

            for target in modules:

                if target == current:
                    continue

                linked = (
                    call == target or
                    call.endswith("." + target) or
                    (call in RUNTIME_PATTERNS and RUNTIME_PATTERNS[call] == target)
                )

                if linked:
                    graph[current].add(target)
                    reverse[target].add(current)
                    weights[current] += 1

    return graph, reverse, weights

# =========================================================
# 🧠 BRAIN
# =========================================================

def find_brain(graph, reverse):

    best, score_best = None, -1

    for n in graph:
        score = len(graph[n]) * 2 + len(reverse[n]) * 3

        if n == "director":
            score += 15
        elif n == "central_decision":
            score += 12
        elif n == "control_panel":
            score += 10
        elif n == "engine":
            score += 8

        if score > score_best:
            best = n
            score_best = score

    return best

# =========================================================
# 🧠 HUBS + LEARNING WEIGHT
# =========================================================

def compute_hubs(graph, reverse, weights, learning_score):

    hubs = []

    for node in graph:

        score = (
            len(graph[node]) * 2 +
            len(reverse[node]) * 2 +
            weights.get(node, 0) +
            learning_score.get(node, 0)
        )

        if score >= 6:
            hubs.append(node)

    return hubs

# =========================================================
# 🧠 ISOLATED
# =========================================================

def compute_isolated(graph, reverse):

    return [n for n in graph if not graph[n] and not reverse[n]]

# =========================================================
# 🧠 DECISION (IMPROVED PRIORITY)
# =========================================================

def decide(hubs, isolated):

    actions = []

    for n in isolated:
        actions.append({
            "type": "connect",
            "target": n,
            "priority": 10,
            "reason": "isolation"
        })

    for n in hubs:
        actions.append({
            "type": "optimize",
            "target": n,
            "priority": 5,
            "reason": "traffic"
        })

    return actions

# =========================================================
# 🧪 VALIDATION
# =========================================================

def validate(files):

    errors = 0

    for f in files:
        try:
            code = read_file(f)
            compile(code, f, "exec")
            ast.parse(code)
        except:
            errors += 1

    return errors

# =========================================================
# 🧠 CYCLE + LEARNING LOOP
# =========================================================

def build_cycle():

    memory = load_memory()
    files, modules = scan()

    log("\n==============================")
    log("🧠 MEGABOT v11 LEARNING LOOP")
    log("==============================")

    graph, reverse, weights = build_runtime_graph(files, modules)

    brain = find_brain(graph, reverse)

    learning = memory.get("learning_score", {})

    hubs = compute_hubs(graph, reverse, weights, learning)
    isolated = compute_isolated(graph, reverse)
    actions = decide(hubs, isolated)

    # =========================
    # 🧠 LEARNING UPDATE
    # =========================

    for a in actions:
        t = a["target"]
        learning[t] = learning.get(t, 0) + 1

    memory["learning_score"] = learning

    # =========================
    # 🧠 GRAPH DRIFT + HASH
    # =========================

    ghash = hash_graph(graph)
    prev_hash = memory.get("graph_hash")

    drift = 1 if prev_hash and prev_hash != ghash else 0

    memory["graph_hash"] = ghash
    memory["drift"] = drift

    save_report(actions, isolated, hubs)

    memory.update({
        "runtime_graph": {k: list(v) for k, v in graph.items()},
        "reverse_graph": {k: list(v) for k, v in reverse.items()},
        "weights": weights,
        "brain_node": brain,
        "hubs": hubs,
        "isolated": isolated,
        "actions": actions
    })

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

    log(f"BRAIN: {brain}")
    log(f"HUBS: {len(hubs)}")
    log(f"ISOLATED: {len(isolated)}")
    log(f"DRIFT: {drift}")

    log("==============================")
    log(f"cycles={memory['cycles']} errors={errors}")

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