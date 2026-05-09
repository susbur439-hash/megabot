# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v8
# 🛡 CORE SAFE + DATA CONTRACT + STABLE RUNTIME
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

# 🛡 SAFE LIMITS
MIN_LIVE_CYCLES_BEFORE_QUARANTINE = 5
MAX_RUNTIME_FAILURES_BEFORE_QUARANTINE = 5

# =========================================================
# 📦 DATA CONTRACT (MEGABOT CORE STANDARD)
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

def enforce_contract(data: dict) -> dict:
    """🛡 гарантирует единый формат данных"""
    if not isinstance(data, dict):
        data = {}

    for k, t in MEGABOT_CONTRACT.items():
        if k not in data:
            data[k] = t()

    return data

# =========================================================
# 🧠 CORE PROTECTION
# =========================================================

CORE_MODULE_KEYWORDS = [
    "control", "core", "brain", "engine", "router",
    "execution", "director", "builder", "memory",
    "planner", "decision", "evaluation", "learning",
    "task", "observer", "run"
]

# =========================================================
# 🧠 MEMORY
# =========================================================

def load_memory():
    default = {
        "cycles": 0,
        "module_age": {},
        "deleted": [],
        "repaired": [],
        "runtime_failed": {},
        "syntax_failed": {},
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
# 📋 LOGGING
# =========================================================

LOGS = []

def log(msg):
    print(msg)
    LOGS.append(str(msg))

# =========================================================
# 🔍 SCAN FIXED
# =========================================================

def scan():
    files = []
    modules = []

    for root, _, file_list in os.walk(ROOT_DIR):

        if ".git" in root or QUARANTINE_DIR in root or "__pycache__" in root:
            continue

        for file in file_list:
            path = os.path.join(root, file)
            files.append(path)

            if os.path.basename(root) == MODULES_DIR and file.endswith(".py"):
                modules.append(file)

    return files, modules

# =========================================================
# 🧠 CORE CHECK
# =========================================================

def is_core(name):
    return any(k in name.lower() for k in CORE_MODULE_KEYWORDS)

# =========================================================
# 📖 FILE READ
# =========================================================

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# =========================================================
# 🧠 DEP GRAPH
# =========================================================

def build_dependencies(files, modules):
    deps = {m: set() for m in modules}

    for f in files:
        if not f.endswith(".py"):
            continue

        content = read_file(f)
        for m in modules:
            name = m.replace(".py", "")
            if f"import {name}" in content or f"from {name}" in content or f"{name}." in content:
                deps[m].add(f)

    return deps

# =========================================================
# 🧠 SCORE
# =========================================================

def module_score(module, deps):
    refs = len(deps.get(module, []))
    return refs * 5 + (10 if refs > 0 else 0)

# =========================================================
# 🛡 QUARANTINE RULE
# =========================================================

def should_quarantine(module, score, deps, age, fail_count):
    if is_core(module):
        return False
    if score > 0:
        return False
    if len(deps.get(module, [])) > 0:
        return False
    if age < MIN_LIVE_CYCLES_BEFORE_QUARANTINE:
        return False
    if fail_count < MAX_RUNTIME_FAILURES_BEFORE_QUARANTINE:
        return False
    return True

# =========================================================
# 📦 QUARANTINE
# =========================================================

def quarantine_file(path):
    try:
        os.makedirs(QUARANTINE_DIR, exist_ok=True)
        dst = os.path.join(QUARANTINE_DIR, os.path.basename(path))
        shutil.move(path, dst)
        log(f"📦 QUARANTINED: {path}")
        return True
    except Exception as e:
        log(f"❌ QUARANTINE ERROR: {e}")
        return False

# =========================================================
# 🏗 TEMPLATE
# =========================================================

def build_template(name):
    pure = name.replace(".py", "")
    return f"""
def run(data=None):
    data = data or {{}}
    data = {{k: v for k, v in data.items()}} if isinstance(data, dict) else {{}}

    data.setdefault("log", [])
    data["log"].append("⚙️ {pure}")

    return data
"""

# =========================================================
# 🔧 REPAIR
# =========================================================

def repair_module(path, memory):
    try:
        name = os.path.basename(path)

        if is_core(name):
            return False

        os.makedirs(BACKUP_DIR, exist_ok=True)
        shutil.copy(path, os.path.join(BACKUP_DIR, name))

        with open(path, "w", encoding="utf-8") as f:
            f.write(build_template(name))

        memory["repaired"].append(path)
        log(f"🔧 REPAIRED: {path}")
        return True

    except Exception as e:
        log(f"❌ REPAIR ERROR: {e}")
        return False

# =========================================================
# 🧪 SYNTAX
# =========================================================

def syntax_test(path):
    try:
        src = read_file(path)
        compile(src, path, "exec")
        ast.parse(src)
        return True, None
    except Exception as e:
        return False, str(e)

# =========================================================
# 🧪 RUNTIME SAFE
# =========================================================

def runtime_test(path):
    try:
        name = os.path.basename(path).replace(".py", "")

        spec = importlib.util.spec_from_file_location(name, path)
        if not spec or not spec.loader:
            return False, "IMPORT FAIL"

        mod = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(mod)

        if not hasattr(mod, "run"):
            return True, "NO RUN"

        test_data = enforce_contract({
            "task": "builder_test",
            "input": {},
            "log": [],
            "experience": [],
            "evaluation": {},
            "create_count": 0,
            "control_state": {},
            "control_bias": {},
            "control_flags": {}
        })

        result = mod.run(test_data)

        if not isinstance(result, dict):
            return False, "INVALID OUTPUT TYPE"

        return True, result

    except Exception as e:
        return False, str(e)

# =========================================================
# 🧪 VALIDATE
# =========================================================

def validate_modules(modules, memory):
    s_fail = r_fail = 0

    log("\n🧪 VALIDATING MODULES")

    for m in modules:
        path = os.path.join(MODULES_DIR, m)

        ok, err = syntax_test(path)
        if not ok:
            s_fail += 1
            memory["syntax_failed"][path] = memory["syntax_failed"].get(path, 0) + 1
            log(f"❌ SYNTAX FAIL: {path} -> {err}")
            repair_module(path, memory)
            continue

        log(f"✅ SYNTAX OK: {path}")

        if ENABLE_RUNTIME_TEST:
            ok2, res = runtime_test(path)
            if not ok2:
                r_fail += 1
                memory["runtime_failed"][path] = memory["runtime_failed"].get(path, 0) + 1
                log(f"⚠️ RUNTIME FAIL: {path} -> {res}")
            else:
                log(f"🚀 RUNTIME OK: {path}")

    return s_fail, r_fail

# =========================================================
# 🧠 CLEANUP
# =========================================================

def cleanup_modules(modules, deps, memory):
    q = 0
    log("\n🗑 CLEANUP")

    for m in modules:
        path = os.path.join(MODULES_DIR, m)

        score = module_score(m, deps)
        age = memory["module_age"].get(m, 0)
        fail = memory["runtime_failed"].get(path, 0)

        if should_quarantine(m, score, deps, age, fail):
            if quarantine_file(path):
                memory["deleted"].append(path)
                q += 1
        else:
            memory["module_age"][m] = age + 1

    return q

# =========================================================
# 📊 REPORT
# =========================================================

def save_report(mem, s, r, q):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "time": time.time(),
            "cycles": mem["cycles"],
            "syntax_failed": s,
            "runtime_failed": r,
            "quarantined": q,
            "logs": LOGS[-300:]
        }, f, indent=2, ensure_ascii=False)

# =========================================================
# 🧠 MAIN
# =========================================================

def build_cycle():

    memory = load_memory()
    files, modules = scan()
    deps = build_dependencies(files, modules)

    log("\n==============================")
    log("🧠 MEGABOT BUILDER v8")
    log("==============================")

    log(f"FILES: {len(files)} | MODULES: {len(modules)}")

    s, r = validate_modules(modules, memory)

    q = 0
    if ENABLE_CLEANUP:
        q = cleanup_modules(modules, deps, memory)

    memory["cycles"] += 1
    memory["history"].append({
        "cycle": memory["cycles"],
        "s": s,
        "r": r,
        "q": q
    })

    save_memory(memory)
    save_report(memory, s, r, q)

    log("\n==============================")
    log("📊 DONE")
    log(f"cycles={memory['cycles']} repaired={len(memory['repaired'])}")
    log(f"runtime_failed={r} syntax_failed={s} quarantined={q}")
    log("==============================")

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
