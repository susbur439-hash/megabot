# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v8.1
# 🛡 CORE SAFE + DATA CONTRACT + STABLE RUNTIME
# 🔥 SAFE TASK PIPELINE + CONTRACT NORMALIZATION
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

MIN_LIVE_CYCLES_BEFORE_QUARANTINE = 5
MAX_RUNTIME_FAILURES_BEFORE_QUARANTINE = 5

# =========================================================
# 📦 DATA CONTRACT
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
# 🛡 CONTRACT NORMALIZATION
# =========================================================

def normalize_contract(data):

    if data is None:
        data = {}

    if not isinstance(data, dict):
        data = {
            "task": str(data)
        }

    normalized = {}

    for key, expected_type in MEGABOT_CONTRACT.items():

        value = data.get(key)

        if isinstance(value, expected_type):
            normalized[key] = value
            continue

        try:
            normalized[key] = expected_type()
        except:
            normalized[key] = None

    # preserve extra fields
    for k, v in data.items():
        if k not in normalized:
            normalized[k] = v

    # safe task
    normalized["task"] = str(
        normalized.get("task", "")
    )

    return normalized

# =========================================================
# 🧠 CORE PROTECTION
# =========================================================

CORE_MODULE_KEYWORDS = [
    "control",
    "core",
    "brain",
    "engine",
    "router",
    "execution",
    "director",
    "builder",
    "memory",
    "planner",
    "decision",
    "evaluation",
    "learning",
    "task",
    "observer",
    "run"
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
        json.dump(
            memory,
            f,
            indent=2,
            ensure_ascii=False
        )

# =========================================================
# 📋 LOGGER
# =========================================================

LOGS = []

def log(message):

    print(message)
    LOGS.append(str(message))

# =========================================================
# 🔍 SCAN
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

            path = os.path.join(root, file)

            files.append(path)

            if os.path.basename(root) == MODULES_DIR:

                if file.endswith(".py"):
                    modules.append(file)

    return files, modules

# =========================================================
# 🧠 CORE CHECK
# =========================================================

def is_core(name):

    lowered = name.lower()

    return any(
        keyword in lowered
        for keyword in CORE_MODULE_KEYWORDS
    )

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
# 🧠 DEPENDENCIES
# =========================================================

def build_dependencies(files, modules):

    deps = {
        module: set()
        for module in modules
    }

    for file in files:

        if not file.endswith(".py"):
            continue

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
# 🧠 MODULE SCORE
# =========================================================

def module_score(module, deps):

    refs = len(
        deps.get(module, [])
    )

    score = refs * 5

    if refs > 0:
        score += 10

    return score

# =========================================================
# 🛡 QUARANTINE RULE
# =========================================================

def should_quarantine(
    module,
    score,
    deps,
    age,
    fail_count
):

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

        os.makedirs(
            QUARANTINE_DIR,
            exist_ok=True
        )

        dst = os.path.join(
            QUARANTINE_DIR,
            os.path.basename(path)
        )

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

    return f'''
def run(data=None):

    if data is None:
        data = {{}}

    if not isinstance(data, dict):
        data = {{
            "task": str(data)
        }}

    data.setdefault("log", [])

    data["log"].append(
        "⚙️ {pure} executed"
    )

    return data
'''

# =========================================================
# 🔧 REPAIR
# =========================================================

def repair_module(path, memory):

    try:

        name = os.path.basename(path)

        if is_core(name):
            return False

        os.makedirs(
            BACKUP_DIR,
            exist_ok=True
        )

        shutil.copy(
            path,
            os.path.join(BACKUP_DIR, name)
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(
                build_template(name)
            )

        memory["repaired"].append(path)

        log(f"🔧 REPAIRED: {path}")

        return True

    except Exception as e:

        log(f"❌ REPAIR ERROR: {e}")

        return False

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
# 🧪 SAFE RUNTIME TEST
# =========================================================

def runtime_test(path):

    try:

        name = os.path.basename(path)
        name = name.replace(".py", "")

        spec = importlib.util.spec_from_file_location(
            name,
            path
        )

        if not spec:
            return False, "SPEC FAIL"

        if not spec.loader:
            return False, "LOADER FAIL"

        mod = importlib.util.module_from_spec(spec)

        old_modules = dict(sys.modules)

        try:

            spec.loader.exec_module(mod)

        finally:

            sys.modules.clear()
            sys.modules.update(old_modules)

        if not hasattr(mod, "run"):
            return True, "NO RUN"

        # =================================================
        # SAFE TEST DATA
        # =================================================

        test_data = normalize_contract({
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

        # =================================================
        # SAFE EXECUTION
        # =================================================

        result = mod.run(test_data)

        # =================================================
        # VALIDATION
        # =================================================

        if result is None:
            return True, "RUN RETURNED NONE"

        if not isinstance(result, dict):
            return False, "INVALID OUTPUT"

        result = normalize_contract(result)

        return True, result

    except Exception as e:

        return False, str(e)

# =========================================================
# 🧪 VALIDATION
# =========================================================

def validate_modules(modules, memory):

    syntax_failed = 0
    runtime_failed = 0

    log("\n🧪 VALIDATING MODULES")

    for module in modules:

        path = os.path.join(
            MODULES_DIR,
            module
        )

        ok, err = syntax_test(path)

        if not ok:

            syntax_failed += 1

            memory["syntax_failed"][path] = (
                memory["syntax_failed"].get(path, 0) + 1
            )

            log(f"❌ SYNTAX FAIL: {path}")
            log(f"   ↳ {err}")

            if ENABLE_AUTOREPAIR:
                repair_module(path, memory)

            continue

        log(f"✅ SYNTAX OK: {path}")

        if ENABLE_RUNTIME_TEST:

            ok2, res = runtime_test(path)

            if not ok2:

                runtime_failed += 1

                memory["runtime_failed"][path] = (
                    memory["runtime_failed"].get(path, 0) + 1
                )

                log(f"⚠️ RUNTIME FAIL: {path}")
                log(f"   ↳ {res}")

            else:

                log(f"🚀 RUNTIME OK: {path}")

    return syntax_failed, runtime_failed

# =========================================================
# 🧠 CLEANUP
# =========================================================

def cleanup_modules(modules, deps, memory):

    q = 0

    log("\n🗑 CLEANUP")

    for module in modules:

        path = os.path.join(
            MODULES_DIR,
            module
        )

        score = module_score(
            module,
            deps
        )

        age = memory["module_age"].get(module, 0)

        fail = memory["runtime_failed"].get(path, 0)

        if should_quarantine(
            module,
            score,
            deps,
            age,
            fail
        ):

            if quarantine_file(path):

                memory["deleted"].append(path)

                q += 1

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

        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False
        )

# =========================================================
# 🧠 MAIN
# =========================================================

def build_cycle():

    memory = load_memory()

    files, modules = scan()

    deps = build_dependencies(
        files,
        modules
    )

    log("\n==============================")
    log("🧠 MEGABOT BUILDER v8.1")
    log("==============================")

    log(
        f"FILES: {len(files)} | "
        f"MODULES: {len(modules)}"
    )

    s, r = validate_modules(
        modules,
        memory
    )

    q = 0

    if ENABLE_CLEANUP:

        q = cleanup_modules(
            modules,
            deps,
            memory
        )

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

    log(
        f"cycles={memory['cycles']} "
        f"repaired={len(memory['repaired'])}"
    )

    log(
        f"runtime_failed={r} "
        f"syntax_failed={s} "
        f"quarantined={q}"
    )

# =========================================================
# ▶ RUN
# =========================================================

if __name__ == "__main__":

    try:

        for _ in range(MAX_CYCLES):
            build_cycle()

    except KeyboardInterrupt:

        log("🛑 STOPPED")

    except Exception as e:

        log(f"FATAL: {e}")

        log(traceback.format_exc())
