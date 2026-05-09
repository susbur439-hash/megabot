# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v8.2 FULL FIXED
# 🛡 ARCHITECTURE + CONNECTION MANAGER + AUTO FIX
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

CONNECTION_FILE = "modules/connection_manager.py"

QUARANTINE_DIR = "quarantine"
BACKUP_DIR = "repair_backups"

MAX_CYCLES = 1

ENABLE_ARCH_COMPILER = True
ENABLE_AUTO_CREATE = True
ENABLE_CONNECTION_CHECK = True
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
# 📖 FILE READ
# =========================================================

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# =========================================================
# 🔍 SCAN FULL REPO
# =========================================================

def scan():
    files = []
    modules = []

    for root, _, files_list in os.walk(ROOT_DIR):

        if ".git" in root:
            continue
        if QUARANTINE_DIR in root:
            continue
        if "__pycache__" in root:
            continue

        for f in files_list:

            if not f.endswith(".py"):
                continue

            path = os.path.join(root, f)
            files.append(path)

            if os.path.basename(root) == MODULES_DIR:
                modules.append(f)

    return files, modules

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
# 🏗 ARCH COMPILER
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
# 🧠 AUTO CREATE MODULE
# =========================================================

def create_module(name):

    path = os.path.join(MODULES_DIR, name + ".py")

    if os.path.exists(path):
        return

    os.makedirs(MODULES_DIR, exist_ok=True)

    code = f"""
def run(data=None):
    if data is None:
        data = {{}}
    data.setdefault("log", [])
    data["log"].append("auto_created:{name}")
    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    log(f"🆕 CREATED MODULE: {name}")

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
# 🧪 SYNTAX
# =========================================================

def syntax_test(path):
    try:
        code = read_file(path)
        compile(code, path, "exec")
        ast.parse(code)
        return True, None
    except Exception as e:
        return False, str(e)

# =========================================================
# 🧪 RUNTIME
# =========================================================

def runtime_test(path):

    try:
        name = os.path.basename(path).replace(".py", "")

        spec = importlib.util.spec_from_file_location(name, path)

        if not spec or not spec.loader:
            return False, "SPEC FAIL"

        mod = importlib.util.module_from_spec(spec)

        old = dict(sys.modules)

        try:
            spec.loader.exec_module(mod)
        finally:
            sys.modules.clear()
            sys.modules.update(old)

        if not hasattr(mod, "run"):
            return True, "NO RUN"

        return True, mod.run({"task": "test"})

    except Exception as e:
        return False, str(e)

# =========================================================
# 🧪 VALIDATION
# =========================================================

def validate(modules, memory):

    s, r = 0, 0

    log("\n🧪 VALIDATION")

    for m in modules:

        path = os.path.join(MODULES_DIR, m)

        ok, err = syntax_test(path)

        if not ok:
            s += 1
            log(f"❌ SYNTAX FAIL {m}: {err}")
            continue

        log(f"✅ OK {m}")

        ok2, res = runtime_test(path)

        if not ok2:
            r += 1
            log(f"⚠️ RUNTIME FAIL {m}: {res}")

    return s, r

# =========================================================
# 🏗 ARCH FIX ENGINE
# =========================================================

def apply_architecture(arch, modules):

    if not arch:
        return

    missing = arch.get("required_modules", [])

    for m in missing:

        file = m + ".py"
        path = os.path.join(MODULES_DIR, file)

        if not os.path.exists(path):
            create_module(m)

# =========================================================
# 🧠 MAIN
# =========================================================

def build_cycle():

    memory = load_memory()

    files, modules = scan()

    arch = load_architecture()

    log("\n==============================")
    log("🧠 MEGABOT v8.2 FULL FIXED")
    log("==============================")

    log(f"FILES: {len(files)} | MODULES: {len(modules)}")

    if ENABLE_CONNECTION_CHECK:
        check_connections()

    result = architecture_compiler(files, modules, arch)

    log(f"\n🏗 ARCH STATUS: {result['status']}")
    log(f"COVERAGE: {result.get('coverage', 0)}%")

    if ENABLE_AUTO_CREATE:
        apply_architecture(arch, modules)

    s, r = validate(modules, memory)

    memory["cycles"] += 1

    memory["history"].append({
        "cycle": memory["cycles"],
        "syntax": s,
        "runtime": r
    })

    save_memory(memory)

    log("\n==============================")
    log("📊 DONE")
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
