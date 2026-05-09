# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v8.2 FULL MERGED
# 🛡 v8.1 ENGINE + v8.2 ARCHITECTURE COMPILER
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
# 📋 LOGGER (FIXED - CRITICAL)
# =========================================================

LOGS = []

def log(message):
    print(message)
    LOGS.append(str(message))

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
# 📖 READ FILE
# =========================================================

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# =========================================================
# 🔍 SCAN FULL REPO (FIXED)
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

            if os.path.basename(root) == MODULES_DIR:
                modules.append(file)

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
# 🏗 ARCHITECTURE COMPILER (v8.2)
# =========================================================

def architecture_compiler(files, modules, arch):

    if not arch:
        return {
            "status": "no_architecture"
        }

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
# 🧪 SYNTAX TEST
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
# 🧪 RUNTIME TEST (SAFE)
# =========================================================

def runtime_test(path):

    try:

        name = os.path.basename(path).replace(".py", "")

        spec = importlib.util.spec_from_file_location(name, path)

        if not spec or not spec.loader:
            return False, "SPEC/LOADER FAIL"

        mod = importlib.util.module_from_spec(spec)

        old = dict(sys.modules)

        try:
            spec.loader.exec_module(mod)
        finally:
            sys.modules.clear()
            sys.modules.update(old)

        if not hasattr(mod, "run"):
            return True, "NO RUN"

        test_data = {
            "task": "builder_test",
            "input": {},
            "log": [],
            "experience": [],
            "evaluation": {},
            "create_count": 0,
            "control_state": {},
            "control_bias": {},
            "control_flags": {}
        }

        result = mod.run(test_data)

        if result is None:
            return True, "NONE"

        if not isinstance(result, dict):
            return False, "INVALID OUTPUT"

        return True, result

    except Exception as e:
        return False, str(e)

# =========================================================
# 🧪 VALIDATION ENGINE
# =========================================================

def validate_modules(modules, memory):

    syntax_failed = 0
    runtime_failed = 0

    log("\n🧪 VALIDATION")

    for module in modules:

        path = os.path.join(MODULES_DIR, module)

        ok, err = syntax_test(path)

        if not ok:
            syntax_failed += 1
            memory["syntax_failed"][path] = memory["syntax_failed"].get(path, 0) + 1
            log(f"❌ SYNTAX FAIL: {path} -> {err}")
            continue

        log(f"✅ SYNTAX OK: {path}")

        ok2, res = runtime_test(path)

        if not ok2:
            runtime_failed += 1
            memory["runtime_failed"][path] = memory["runtime_failed"].get(path, 0) + 1
            log(f"⚠️ RUNTIME FAIL: {path} -> {res}")
        else:
            log(f"🚀 RUNTIME OK: {path}")

    return syntax_failed, runtime_failed

# =========================================================
# 🧠 CLEANUP
# =========================================================

def cleanup_modules(modules, memory):

    q = 0

    log("\n🗑 CLEANUP")

    for module in modules:

        path = os.path.join(MODULES_DIR, module)

        age = memory["module_age"].get(module, 0)
        fail = memory["runtime_failed"].get(path, 0)

        if age > 5 and fail > 3:

            try:

                os.makedirs(QUARANTINE_DIR, exist_ok=True)

                shutil.move(path, os.path.join(QUARANTINE_DIR, module))

                memory["deleted"].append(path)

                log(f"📦 QUARANTINED: {path}")

                q += 1

            except Exception as e:
                log(f"❌ QUARANTINE ERROR: {e}")

        else:
            memory["module_age"][module] = age + 1

    return q

# =========================================================
# 📊 REPORT
# =========================================================

def save_report(memory, s, r, q):

    report = {
        "time": time.time(),
        "cycles": memory["cycles"],
        "syntax_failed": s,
        "runtime_failed": r,
        "quarantined": q,
        "logs": LOGS[-300:]
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

# =========================================================
# 🧠 MAIN CYCLE
# =========================================================

def build_cycle():

    memory = load_memory()

    files, modules = scan()

    arch = load_architecture()

    log("\n==============================")
    log("🧠 MEGABOT BUILDER v8.2 FULL MERGED")
    log("==============================")

    log(f"FILES: {len(files)} | MODULES: {len(modules)}")

    # =========================
    # 🏗 ARCHITECTURE
    # =========================

    if ENABLE_ARCH_COMPILER:

        result = architecture_compiler(files, modules, arch)

        log("\n🏗 ARCHITECTURE COMPILER")
        log(f"STATUS: {result['status']}")
        log(f"COVERAGE: {result.get('coverage', 0)}%")

        if result.get("missing_modules"):
            log(f"❌ MISSING: {result['missing_modules']}")

        if result.get("extra_modules"):
            log(f"⚠️ EXTRA: {result['extra_modules']}")

    # =========================
    # 🧪 VALIDATION
    # =========================

    s, r = validate_modules(modules, memory)

    q = 0

    if ENABLE_CLEANUP:
        q = cleanup_modules(modules, memory)

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
