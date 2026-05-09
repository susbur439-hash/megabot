# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v8.2
# 🧠 FULL REPOSITORY + ARCHITECTURE COMPILER
# =========================================================

import os
import json
import traceback
import shutil
import importlib.util
import ast
import time
import sys

# =========================================================
# ⚙ CONFIG
# =========================================================

ROOT_DIR = "."
MODULES_DIR = "modules"

ARCH_FILE = "architecture.json"

MEMORY_FILE = "builder_memory.json"
REPORT_FILE = "builder_report.json"

QUARANTINE_DIR = "quarantine"
BACKUP_DIR = "repair_backups"

MAX_CYCLES = 1

ENABLE_CLEANUP = True
ENABLE_QUARANTINE = True
ENABLE_AUTOREPAIR = True
ENABLE_RUNTIME_TEST = True
ENABLE_SYNTAX_TEST = True
ENABLE_ARCH_COMPILER = True

# =========================================================
# 📦 CONTRACT
# =========================================================

MEGABOT_CONTRACT = {
    "task": str,
    "input": dict,
    "log": list,
    "experience": list,
    "evaluation": dict,
    "create_count": int,
    "control_state": dict,
    "control_bias": dict,
    "control_flags": dict
}

# =========================================================
# 🧠 ARCHITECTURE LOADER
# =========================================================

def load_architecture():

    if not os.path.exists(ARCH_FILE):
        return None

    try:
        with open(ARCH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

# =========================================================
# 🧠 FULL REPO SCAN (FIXED)
# =========================================================

def scan():

    files = []
    modules = []

    for root, _, file_list in os.walk(ROOT_DIR):

        if ".git" in root:
            continue
        if QUARANTINE_DIR in root:
            continue
        if "__pycache__" in root:
            continue

        for file in file_list:

            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)
            files.append(path)

            # modules ONLY in modules dir
            if MODULES_DIR in root:
                modules.append(file)

    return files, modules

# =========================================================
# 🧠 ARCHITECTURE COMPILER
# =========================================================

def architecture_compiler(repo_files, modules, arch):

    if not arch:
        return {}

    required = set(arch.get("required_modules", []))
    existing = set([m.replace(".py", "") for m in modules])

    missing = required - existing
    extra = existing - required

    return {
        "missing_modules": list(missing),
        "extra_modules": list(extra),
        "status": "ok" if not missing else "incomplete"
    }

# =========================================================
# 🧠 GLOBAL DEP GRAPH
# =========================================================

def build_dependencies(files, modules):

    deps = {m: set() for m in modules}

    for file in files:

        content = read_file(file)

        for module in modules:

            name = module.replace(".py", "")

            if (
                f"import {name}" in content
                or f"from {name}" in content
                or f"{name}." in content
            ):
                deps[module].add(file)

    return deps

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
# 🧠 MAIN
# =========================================================

def build_cycle():

    memory = load_memory()

    files, modules = scan()

    arch = load_architecture()

    deps = build_dependencies(files, modules)

    log("\n==============================")
    log("🧠 MEGABOT BUILDER v8.2")
    log("==============================")

    log(f"FILES: {len(files)} | MODULES: {len(modules)}")

    # =====================================================
    # 🧠 ARCHITECTURE ANALYSIS
    # =====================================================

    if ENABLE_ARCH_COMPILER:

        result = architecture_compiler(files, modules, arch)

        log("\n🏗 ARCHITECTURE COMPILER")

        log(f"STATUS: {result.get('status')}")

        if result.get("missing_modules"):

            log(f"❌ MISSING: {result['missing_modules']}")

        if result.get("extra_modules"):

            log(f"⚠️ EXTRA: {result['extra_modules']}")

    # =====================================================
    # 🧪 VALIDATION
    # =====================================================

    s, r = validate_modules(modules, memory)

    q = 0

    if ENABLE_CLEANUP:
        q = cleanup_modules(modules, deps, memory)

    memory["cycles"] += 1

    memory["history"].append({
        "cycle": memory["cycles"],
        "syntax_failed": s,
        "runtime_failed": r,
        "quarantined": q
    })

    save_memory(memory)
    save_report(memory, s, r, q)

    log("\n==============================")
    log("📊 DONE")
    log("==============================")

    log(f"cycles={memory['cycles']} repaired={len(memory['repaired'])}")
    log(f"runtime_failed={r} syntax_failed={s} quarantined={q}")

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
