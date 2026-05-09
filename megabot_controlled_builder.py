# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v8.3
# 🧠 FULL REPOSITORY + CONNECTION BRAIN + ARCH COMPILER
# =========================================================

import os
import json
import traceback
import importlib.util
import ast
import sys
import time

# =========================================================
# ⚙ CONFIG
# =========================================================

ROOT_DIR = "."
MODULES_DIR = "modules"

ARCH_FILE = "architecture.json"
CONNECTION_FILE = "modules/connection_manager.py"

MEMORY_FILE = "builder_memory.json"
REPORT_FILE = "builder_report.json"

MAX_CYCLES = 1

ENABLE_ARCH_COMPILER = True
ENABLE_CONNECTION_BRAIN = True
ENABLE_AUTO_CREATE = True
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
# 🔍 SCAN REPOSITORY
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
# 🔗 CONNECTION BRAIN (NEW CORE)
# =========================================================

def build_connection_graph(files, modules):

    graph = {m: set() for m in modules}

    for file in files:

        code = read_file(file)

        for module in modules:

            name = module.replace(".py", "")

            if (
                f"import {name}" in code
                or f"from {name}" in code
                or f"{name}." in code
            ):
                graph[module].add(name)

    return graph

# =========================================================
# 🧠 ANALYZE CONNECTIONS
# =========================================================

def analyze_graph(graph):

    hubs = []
    isolated = []

    for node, edges in graph.items():

        if len(edges) >= 3:
            hubs.append(node)

        if len(edges) == 0:
            isolated.append(node)

    return hubs, isolated

# =========================================================
# 🔗 CONNECTION MANAGER CHECK
# =========================================================

def check_connections():

    if not os.path.exists(CONNECTION_FILE):
        log("⚠️ connection_manager NOT FOUND")
        return False

    log("🔗 connection_manager OK")
    return True

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
# 🧪 VALIDATION (MINIMAL)
# =========================================================

def validate(modules):

    s = r = 0

    for m in modules:

        path = os.path.join(MODULES_DIR, m)

        try:
            code = read_file(path)
            compile(code, path, "exec")
            ast.parse(code)
        except:
            s += 1

    return s, r

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
    log("🧠 MEGABOT v8.3 FULL BRAIN")
    log("==============================")

    log(f"FILES: {len(files)} | MODULES: {len(modules)}")

    # =========================
    # 🔗 CONNECTION BRAIN
    # =========================

    if ENABLE_CONNECTION_BRAIN:

        graph = build_connection_graph(files, modules)
        hubs, isolated = analyze_graph(graph)

        memory["connections"] = {k: list(v) for k, v in graph.items()}
        memory["hubs"] = hubs
        memory["isolated"] = isolated

        log("\n🔗 CONNECTION BRAIN")
        log(f"HUBS: {hubs}")
        log(f"ISOLATED: {isolated}")

    # =========================
    # 🏗 ARCHITECTURE
    # =========================

    result = architecture_compiler(files, modules, arch)

    log(f"\n🏗 ARCH STATUS: {result['status']}")
    log(f"COVERAGE: {result.get('coverage', 0)}%")

    # =========================
    # 🔗 CONNECTION CHECK
    # =========================

    check_connections()

    # =========================
    # 🧪 VALIDATION
    # =========================

    s, r = validate(modules)

    memory["cycles"] += 1

    memory["history"].append({
        "cycle": memory["cycles"],
        "syntax": s,
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
