# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v3 (CORE SAFE ARCH)
# =========================================================

import os
import json
import traceback

ROOT_DIR = "."
MODULES_DIR = "modules"

MEMORY_FILE = "builder_memory.json"

MAX_CYCLES = 1

ENABLE_CLEANUP = True
ENABLE_SAFE_DELETE = True

MIN_LIVE_CYCLES_BEFORE_DELETE = 2

# =========================================================
# 🧠 CORE PROTECTION LAYER
# =========================================================

CORE_MODULE_KEYWORDS = [
    "control",
    "core",
    "brain",
    "engine",
    "router",
    "execution",
    "director",
]

# =========================================================
# 🧠 MEMORY
# =========================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "cycles": 0,
            "module_age": {},
            "deleted": []
        }

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "cycles": 0,
            "module_age": {},
            "deleted": []
        }


def save_memory(m):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)

# =========================================================
# 📋 LOG
# =========================================================

def log(x):
    print(x)

# =========================================================
# 🔍 SCAN
# =========================================================

def scan():
    files = []
    modules = []

    for r, d, f in os.walk(ROOT_DIR):
        if ".git" in r:
            continue

        for file in f:
            path = os.path.join(r, file)
            files.append(path)

            if r.endswith("modules"):
                modules.append(file)

    return files, modules

# =========================================================
# 🧠 CORE CHECK
# =========================================================

def is_core(module_name):
    name = module_name.lower()

    return any(k in name for k in CORE_MODULE_KEYWORDS)

# =========================================================
# 🧠 DEPENDENCY GRAPH
# =========================================================

def build_dependencies(files, modules):
    deps = {m: set() for m in modules}

    for file in files:
        if not file.endswith(".py"):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                c = f.read()

            for m in modules:
                name = m.replace(".py", "")

                if f"import {name}" in c or f"from {name}" in c:
                    deps[m].add(file)

                if f"{name}." in c:
                    deps[m].add(file)

        except:
            continue

    return deps

# =========================================================
# 🧠 MODULE VALUE SCORE (IMPROVED)
# =========================================================

def module_score(module, deps):
    score = 0

    if module in deps:
        score += len(deps[module]) * 3

    if len(deps.get(module, [])) > 0:
        score += 5

    return score

# =========================================================
# 🛑 SAFE DELETE RULE (STRONG PROTECTION)
# =========================================================

def should_delete(module, score, deps, age):

    # ❌ NEVER DELETE CORE
    if is_core(module):
        return False

    # ❌ still used
    if score > 0:
        return False

    # ❌ has dependencies
    if len(deps.get(module, [])) > 0:
        return False

    # ❌ not stable long enough
    if age < MIN_LIVE_CYCLES_BEFORE_DELETE:
        return False

    return True

# =========================================================
# 🗑 DELETE SAFE
# =========================================================

def delete(path):
    if not ENABLE_SAFE_DELETE:
        return False

    try:
        if os.path.exists(path):
            os.remove(path)
            log(f"🗑 DELETED SAFE: {path}")
            return True
    except Exception as e:
        log(f"❌ DELETE ERROR: {e}")

    return False

# =========================================================
# 🧠 MAIN CYCLE
# =========================================================

def build_cycle():

    memory = load_memory()

    files, modules = scan()
    deps = build_dependencies(files, modules)

    log("\n=================================================")
    log("🧠 MEGABOT BUILDER v3 (CORE SAFE)")
    log("=================================================")

    log(f"📦 FILES: {len(files)}")
    log(f"🧩 MODULES: {len(modules)}")

    if ENABLE_CLEANUP:

        log("\n🗑 CLEANUP CHECK:")

        for m in modules:

            path = os.path.join(MODULES_DIR, m)

            score = module_score(m, deps)
            age = memory["module_age"].get(m, 0)

            if should_delete(m, score, deps, age):

                log(f" - DELETE CANDIDATE: {path} | score={score}")

                if delete(path):
                    memory["deleted"].append(path)

            else:
                memory["module_age"][m] = age + 1

    memory["cycles"] += 1

    save_memory(memory)

    log("\n=================================================")
    log("📊 DONE")
    log("=================================================")

    log(f"🧠 cycles: {memory['cycles']}")
    log(f"🗑 deleted: {len(memory['deleted'])}")

# =========================================================
# ▶️ RUN
# =========================================================

if __name__ == "__main__":
    try:
        for _ in range(MAX_CYCLES):
            build_cycle()

    except Exception as e:
        log("❌ FATAL")
        log(str(e))
        log(traceback.format_exc())
