# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v8.3 FIXED
# 🧠 FULL REPOSITORY + AST CONNECTION BRAIN + ARCH BRAIN CORE
# =========================================================

import os
import json
import traceback
import importlib.util
import ast
import sys
import time

from modules.architecture_brain import analyze  # 🔥 INTEGRATION

# =========================================================
# ⚙ CONFIG
# =========================================================

ROOT_DIR = "."
MODULES_DIR = "modules"

ARCH_FILE = "architecture.json"

MEMORY_FILE = "builder_memory.json"
REPORT_FILE = "builder_report.json"

MAX_CYCLES = 1

ENABLE_CONNECTION_BRAIN = True
ENABLE_ARCH_BRAIN = True
ENABLE_ARCH_COMPILER = True
ENABLE_RUNTIME_TEST = True
ENABLE_SYNTAX_TEST = True

# =========================================================
# 📋 LOGGER
# =========================================================

LOGS = []

def log(msg):
    print(msg)
    LOGS.append(str(msg))

# =========================================================
# 💾 MEMORY
# =========================================================

def load_memory():
    default = {
        "cycles": 0,
        "connections": {},
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
# 📖 READ FILE
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
                modules.append(f)

    return files, modules

# =========================================================
# 🧠 AST CONNECTION BRAIN
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
# 🔗 GRAPH BUILDER
# =========================================================

def build_connection_graph(files, modules):

    graph = {m: set() for m in modules}
    weights = {m: 0 for m in modules}

    for file in files:

        code = read_file(file)
        imports = extract_imports(code)

        for module in modules:

            name = module.replace(".py", "")

            if name in imports:
                graph[module].add(name)
                weights[module] += 1

    return graph, weights

# =========================================================
# 🧠 ARCH BRAIN INTEGRATION (🔥 MAIN ADDITION)
# =========================================================

def run_architecture_brain(files):

    result = analyze(files)

    return {
        "graph": result["graph"],
        "roles": result["roles"],
        "brain_node": result["brain"],
        "hubs": result["hubs"],
        "isolated": result["isolated"]
    }

# =========================================================
# 🧠 ARCH COMPILER
# =========================================================

def architecture_compiler(files, modules, arch):

    if not arch:
        return {"status": "no_architecture"}

    required = set(arch.get("required_modules", []))
    existing = set([m.replace(".py", "") for m in modules])

    missing = required - existing
    extra = existing - required

    return {
        "status": "ok" if not missing else "incomplete",
        "missing_modules": list(missing),
        "extra_modules": list(extra),
        "coverage": round(len(existing & required) / max(len(required), 1) * 100, 2)
    }

# =========================================================
# 🧪 VALIDATION
# =========================================================

def validate(modules):

    s = 0

    for m in modules:

        path = os.path.join(MODULES_DIR, m)

        try:
            code = read_file(path)
            compile(code, path, "exec")
            ast.parse(code)
        except:
            s += 1

    return s

# =========================================================
# 🧠 MAIN CYCLE
# =========================================================

def build_cycle():

    memory = load_memory()

    files, modules = scan()

    arch = None
    if os.path.exists(ARCH_FILE):
        with open(ARCH_FILE, "r", encoding="utf-8") as f:
            arch = json.load(f)

    log("\n==============================")
    log("🧠 MEGABOT v8.3 FIXED BRAIN")
    log("==============================")

    log(f"FILES: {len(files)} | MODULES: {len(modules)}")

    # =========================
    # 🔗 CONNECTION BRAIN
    # =========================

    if ENABLE_CONNECTION_BRAIN:

        graph, weights = build_connection_graph(files, modules)

        memory["connections"] = {k: list(v) for k, v in graph.items()}
        memory["weights"] = weights

    # =========================
    # 🧠 ARCH BRAIN (NEW CORE)
    # =========================

    if ENABLE_ARCH_BRAIN:

        brain = run_architecture_brain(files)

        memory["roles"] = brain["roles"]
        memory["brain_node"] = brain["brain_node"]
        memory["hubs"] = brain["hubs"]
        memory["isolated"] = brain["isolated"]

        log("\n🧠 ARCHITECTURE BRAIN")
        log(f"BRAIN NODE: {brain['brain_node']}")
        log(f"HUBS: {brain['hubs']}")
        log(f"ISOLATED: {brain['isolated']}")

    # =========================
    # 🏗 ARCH COMPILER
    # =========================

    result = architecture_compiler(files, modules, arch)

    log(f"\n🏗 ARCH STATUS: {result['status']}")
    log(f"COVERAGE: {result.get('coverage', 0)}%")

    # =========================
    # 🧪 VALIDATION
    # =========================

    s = validate(modules)

    memory["cycles"] += 1

    memory["history"].append({
        "cycle": memory["cycles"],
        "syntax_failed": s,
        "brain_node": memory.get("brain_node"),
        "hubs": len(memory["hubs"]),
        "isolated": len(memory["isolated"])
    })

    save_memory(memory)

    log("\n==============================")
    log("📊 DONE")
    log("==============================")

    log(f"cycles={memory['cycles']}")
    log(f"syntax_failed={s}")

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
