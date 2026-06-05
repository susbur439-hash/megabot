import os
import json
import traceback
import ast
import hashlib

from modules.control_bus import emit

# 🧠 AI LAYER (SAFE)
try:
    from modules.ai_gateway import ask_model
except:
    ask_model = None

# =========================================================
# ⚙ CONFIG
# =========================================================

ROOT_DIR = "."
MODULES_DIR = "modules"

MEMORY_FILE = "builder_memory.json"

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
# 📋 LOG
# =========================================================

def log(msg):
    print(msg)

# =========================================================
# 🔐 GRAPH HASH
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
        "learning_score": {},
        "ai_report": {},
        "ai_score": 0
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
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except:
        pass

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
# 🔍 ANALYSIS
# =========================================================

def extract_imports(code):
    imports = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except:
        pass
    return imports


def extract_runtime_calls(code):
    calls = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
    except:
        pass
    return calls

# =========================================================
# 🤖 AI ANALYSIS (FIXED + SAFE)
# =========================================================

def ai_analyze(graph, reverse, hubs, isolated, brain):

    if not ask_model:
        return {
            "score": 0,
            "status": "no_ai_gateway"
        }

    prompt = f"""
Ты архитектор системы Megabot.

Дай строгий анализ:

- архитектурные проблемы
- слабые места
- избыточные модули
- улучшения
- оценка качества 0-100 (обязательно)

BRAIN: {brain}
HUBS: {hubs}
ISOLATED: {isolated}

GRAPH:
{json.dumps(graph, indent=2)}
"""

    try:
        result = ask_model(prompt)

        # 🔧 FIX: нормализация ответа
        if isinstance(result, dict):
            if "score" not in result:
                result["score"] = 0
            return result

        return {"score": 0, "raw": str(result)}

    except Exception as e:
        return {
            "score": 0,
            "error": str(e)
        }

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

        refs = extract_runtime_calls(code) + extract_imports(code)

        for ref in refs:
            for target in modules:

                if target == current:
                    continue

                if target in ref:
                    graph[current].add(target)
                    reverse[target].add(current)
                    weights[current] += 1

    return graph, reverse, weights

# =========================================================
# 🧠 BRAIN
# =========================================================

def find_brain(graph, reverse, memory):

    best, best_score = None, -1
    bias = 0

    for n in graph:

        score = len(graph[n]) + len(reverse[n])

        if n == "director":
            score += 20

        score += bias

        if score > best_score:
            best = n
            best_score = score

    return best

# =========================================================
# 🧠 HUBS
# =========================================================

def compute_hubs(graph, reverse, weights, learning):

    hubs = []

    for n in graph:
        score = len(graph[n]) + len(reverse[n]) + weights.get(n, 0)

        if score >= 3:
            hubs.append(n)

    return hubs

# =========================================================
# 🧠 ISOLATED
# =========================================================

def compute_isolated(graph, reverse):
    return [n for n in graph if not graph[n] and not reverse[n]]

# =========================================================
# 🧠 DECISION
# =========================================================

def decide(hubs, isolated):

    actions = []

    for n in isolated:
        actions.append({"type": "connect", "target": n})

    for n in hubs:
        actions.append({"type": "optimize", "target": n})

    return actions

# =========================================================
# 🧪 VALIDATION
# =========================================================

def validate(files):
    errors = 0
    for f in files:
        try:
            ast.parse(read_file(f))
        except:
            errors += 1
    return errors

# =========================================================
# 🧠 CYCLE
# =========================================================

def build_cycle():

    memory = load_memory()

    files = []
    modules = []

    for root, _, file_list in os.walk(ROOT_DIR):

        if ".git" in root or "__pycache__" in root:
            continue

        for f in file_list:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                files.append(path)

                if os.path.basename(root) == MODULES_DIR:
                    name = f.replace(".py", "")
                    if name in CORE_MODULES:
                        modules.append(name)

    log("\n==============================")
    log("🧠 MEGABOT v13 AI CONTROL LOOP (FIXED)")
    log("==============================")

    graph, reverse, weights = build_runtime_graph(files, modules)

    brain = find_brain(graph, reverse, memory)

    hubs = compute_hubs(graph, reverse, weights, memory.get("learning_score", {}))
    isolated = compute_isolated(graph, reverse)
    actions = decide(hubs, isolated)

    # 🤖 AI CALL
    ai_report = ai_analyze(graph, reverse, hubs, isolated, brain)

    memory["ai_report"] = ai_report
    memory["ai_score"] = ai_report.get("score", 0)

    errors = validate(files)

    memory["cycles"] += 1
    memory["brain_node"] = brain
    memory["hubs"] = hubs
    memory["isolated"] = isolated
    memory["actions"] = actions
    memory["graph_hash"] = hash_graph(graph)

    log(f"BRAIN: {brain}")
    log(f"HUBS: {len(hubs)}")
    log(f"ISOLATED: {len(isolated)}")
    log(f"AI_SCORE: {memory['ai_score']}")
    log(f"ERRORS: {errors}")
    log("==============================")

    save_memory(memory)

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