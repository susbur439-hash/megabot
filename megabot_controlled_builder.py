# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v7
# 🛡 CORE SAFE + SMART VALIDATION + SAFE AUTOFIX
# 🔥 STABLE RUNTIME + SAFE IMPORT SYSTEM
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

ENABLE_DEPENDENCY_GRAPH = True

# 🛡 SAFE LIMITS
MIN_LIVE_CYCLES_BEFORE_QUARANTINE = 5
MAX_RUNTIME_FAILURES_BEFORE_QUARANTINE = 5

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
    "run",
]

# =========================================================
# 🧠 MEMORY
# =========================================================

def load_memory():

    default_memory = {
        "cycles": 0,
        "module_age": {},
        "deleted": [],
        "repaired": [],
        "runtime_failed": {},
        "syntax_failed": {},
        "history": []
    }

    if not os.path.exists(MEMORY_FILE):
        return default_memory

    try:

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        for k, v in default_memory.items():
            loaded.setdefault(k, v)

        return loaded

    except:
        return default_memory


def save_memory(memory):

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

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

    for root, dirs, file_list in os.walk(ROOT_DIR):

        if ".git" in root:
            continue

        if QUARANTINE_DIR in root:
            continue

        if "__pycache__" in root:
            continue

        for file in file_list:

            path = os.path.join(root, file)

            files.append(path)

            if root.endswith("modules") and file.endswith(".py"):
                modules.append(file)

    return files, modules

# =========================================================
# 🧠 CORE CHECK
# =========================================================

def is_core(module_name):

    lowered = module_name.lower()

    return any(
        keyword in lowered
        for keyword in CORE_MODULE_KEYWORDS
    )

# =========================================================
# 📖 SAFE FILE READ
# =========================================================

def read_file(path):

    try:

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    except:
        return ""

# =========================================================
# 🧠 DEPENDENCY GRAPH
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

        if not content:
            continue

        for module in modules:

            name = module.replace(".py", "")

            try:

                if f"import {name}" in content:
                    deps[module].add(file)

                if f"from {name}" in content:
                    deps[module].add(file)

                if f"{name}." in content:
                    deps[module].add(file)

            except:
                continue

    return deps

# =========================================================
# 🧠 MODULE SCORE
# =========================================================

def module_score(module, deps):

    refs = len(deps.get(module, []))

    score = 0

    score += refs * 5

    if refs > 0:
        score += 10

    return score

# =========================================================
# 🧠 SAFE QUARANTINE RULE
# =========================================================

def should_quarantine(
    module,
    score,
    deps,
    age,
    runtime_fail_count
):

    if is_core(module):
        return False

    if score > 0:
        return False

    if len(deps.get(module, [])) > 0:
        return False

    if age < MIN_LIVE_CYCLES_BEFORE_QUARANTINE:
        return False

    if runtime_fail_count < MAX_RUNTIME_FAILURES_BEFORE_QUARANTINE:
        return False

    return True

# =========================================================
# 📦 QUARANTINE
# =========================================================

def quarantine_file(path):

    try:

        os.makedirs(QUARANTINE_DIR, exist_ok=True)

        filename = os.path.basename(path)

        dst = os.path.join(
            QUARANTINE_DIR,
            filename
        )

        shutil.move(path, dst)

        log(f"📦 QUARANTINED: {path}")

        return True

    except Exception as e:

        log(f"❌ QUARANTINE ERROR: {e}")

        return False

# =========================================================
# 🏗 SAFE TEMPLATE
# =========================================================

def build_template(module_name):

    pure = module_name.replace(".py", "")

    return f'''# =========================================================
# 🧠 SAFE AUTO-REPAIRED MODULE: {pure}
# =========================================================

def run(data=None):

    if data is None:
        data = {{}}

    if not isinstance(data, dict):
        data = {{
            "input": str(data)
        }}

    data.setdefault("log", [])

    data["log"].append("⚙️ {pure} executed")

    return data
'''

# =========================================================
# 🔧 SAFE REPAIR
# =========================================================

def repair_module(path, memory):

    try:

        filename = os.path.basename(path)

        if is_core(filename):

            log(f"🛡 SKIPPED CORE REPAIR: {path}")
            return False

        os.makedirs(BACKUP_DIR, exist_ok=True)

        backup_path = os.path.join(
            BACKUP_DIR,
            filename
        )

        shutil.copy(path, backup_path)

        with open(path, "w", encoding="utf-8") as f:
            f.write(build_template(filename))

        memory["repaired"].append(path)

        log(f"🔧 REPAIRED: {path}")

        return True

    except Exception as e:

        log(f"❌ REPAIR ERROR: {path}")
        log(str(e))

        return False

# =========================================================
# 🧪 SYNTAX TEST
# =========================================================

def syntax_test(path):

    try:

        source = read_file(path)

        compile(source, path, "exec")

        ast.parse(source)

        return True, None

    except Exception as e:

        return False, str(e)

# =========================================================
# 🧪 SAFE RUNTIME TEST
# =========================================================

def runtime_test(path):

    try:

        module_name = os.path.basename(path)
        module_name = module_name.replace(".py", "")

        spec = importlib.util.spec_from_file_location(
            module_name,
            path
        )

        if spec is None:
            return False, "SPEC LOAD FAILED"

        if spec.loader is None:
            return False, "LOADER FAILED"

        mod = importlib.util.module_from_spec(spec)

        # 🛡 SAFE IMPORT
        old_modules = dict(sys.modules)

        try:

            spec.loader.exec_module(mod)

        finally:

            sys.modules.clear()
            sys.modules.update(old_modules)

        # =================================================
        # NO RUN
        # =================================================

        if not hasattr(mod, "run"):

            return True, "NO RUN FUNCTION"

        # =================================================
        # SAFE TEST DATA
        # =================================================

        test_data = {
            "task": "builder_test",
            "input": {},
            "log": [],
            "experience": [],
            "evaluation": {},
            "create_count": 0,
            "control_state": {
                "mode": "normal",
                "phase": "init",
                "trend": "stable",
                "energy": 100,
                "cycle": 0,
                "health": 100,
                "stability": 1.0
            },
            "control_bias": {
                "success": 0,
                "fail": 0,
                "create": 0,
                "run": 0
            },
            "control_flags": {
                "loop_detected": False,
                "stagnation": False,
                "overcreate": False
            }
        }

        # =================================================
        # SAFE EXECUTION
        # =================================================

        result = mod.run(test_data)

        # =================================================
        # SAFE VALIDATION
        # =================================================

        if result is None:
            return True, "RUN RETURNED NONE"

        if not isinstance(result, dict):
            return False, f"INVALID RETURN TYPE: {type(result)}"

        return True, result

    except Exception as e:

        return False, str(e)

# =========================================================
# 🧠 VALIDATION
# =========================================================

def validate_modules(modules, memory):

    syntax_failed = 0
    runtime_failed = 0

    log("")
    log("🧪 VALIDATING MODULES")

    for module in modules:

        path = os.path.join(
            MODULES_DIR,
            module
        )

        # =================================================
        # SYNTAX
        # =================================================

        if ENABLE_SYNTAX_TEST:

            ok, err = syntax_test(path)

            if not ok:

                syntax_failed += 1

                memory["syntax_failed"].setdefault(path, 0)
                memory["syntax_failed"][path] += 1

                log(f"❌ SYNTAX FAIL: {path}")
                log(f"   ↳ {err}")

                if ENABLE_AUTOREPAIR:
                    repair_module(path, memory)

                continue

            log(f"✅ SYNTAX OK: {path}")

        # =================================================
        # RUNTIME
        # =================================================

        if ENABLE_RUNTIME_TEST:

            ok_runtime, runtime_result = runtime_test(path)

            if not ok_runtime:

                runtime_failed += 1

                memory["runtime_failed"].setdefault(path, 0)
                memory["runtime_failed"][path] += 1

                log(f"⚠️ RUNTIME FAIL: {path}")
                log(f"   ↳ {runtime_result}")

            else:

                log(f"🚀 RUNTIME OK: {path}")

    return syntax_failed, runtime_failed

# =========================================================
# 🧠 CLEANUP
# =========================================================

def cleanup_modules(modules, deps, memory):

    quarantined = 0

    log("")
    log("🗑 CLEANUP CHECK")

    for module in modules:

        path = os.path.join(
            MODULES_DIR,
            module
        )

        score = module_score(module, deps)

        age = memory["module_age"].get(module, 0)

        runtime_fail_count = memory[
            "runtime_failed"
        ].get(path, 0)

        if should_quarantine(
            module,
            score,
            deps,
            age,
            runtime_fail_count
        ):

            log(
                f"⚠️ UNUSED MODULE: {path}"
            )

            if ENABLE_QUARANTINE:

                if quarantine_file(path):

                    memory["deleted"].append(path)

                    quarantined += 1

        else:

            memory["module_age"][module] = age + 1

    return quarantined

# =========================================================
# 📊 REPORT
# =========================================================

def save_report(
    memory,
    syntax_failed,
    runtime_failed,
    quarantined
):

    report = {
        "timestamp": time.time(),
        "cycles": memory["cycles"],
        "repaired": len(memory["repaired"]),
        "runtime_failed": runtime_failed,
        "syntax_failed": syntax_failed,
        "quarantined": quarantined,
        "logs": LOGS[-500:]
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False
        )

# =========================================================
# 🧠 MAIN BUILD CYCLE
# =========================================================

def build_cycle():

    memory = load_memory()

    files, modules = scan()

    deps = build_dependencies(
        files,
        modules
    )

    log("")
    log("=================================================")
    log("🧠 MEGABOT BUILDER v7")
    log("=================================================")

    log(f"📦 FILES: {len(files)}")
    log(f"🧩 MODULES: {len(modules)}")

    # =====================================================
    # 🧪 VALIDATION
    # =====================================================

    syntax_failed, runtime_failed = validate_modules(
        modules,
        memory
    )

    # =====================================================
    # 🗑 CLEANUP
    # =====================================================

    quarantined = 0

    if ENABLE_CLEANUP:

        quarantined = cleanup_modules(
            modules,
            deps,
            memory
        )

    # =====================================================
    # 💾 MEMORY
    # =====================================================

    memory["cycles"] += 1

    memory["history"].append({
        "cycle": memory["cycles"],
        "syntax_failed": syntax_failed,
        "runtime_failed": runtime_failed,
        "quarantined": quarantined,
    })

    save_memory(memory)

    # =====================================================
    # 📊 REPORT
    # =====================================================

    save_report(
        memory,
        syntax_failed,
        runtime_failed,
        quarantined
    )

    # =====================================================
    # 📊 FINAL
    # =====================================================

    log("")
    log("=================================================")
    log("📊 BUILD FINISHED")
    log("=================================================")

    log(f"🧠 cycles: {memory['cycles']}")
    log(f"🔧 repaired: {len(memory['repaired'])}")
    log(f"⚠️ runtime failed: {runtime_failed}")
    log(f"❌ syntax failed: {syntax_failed}")
    log(f"📦 quarantined: {quarantined}")

    log("")
    log("✅ DONE")

# =========================================================
# ▶️ RUN
# =========================================================

if __name__ == "__main__":

    try:

        for _ in range(MAX_CYCLES):

            build_cycle()

    except KeyboardInterrupt:

        log("🛑 STOPPED")

    except Exception as e:

        log("❌ FATAL ERROR")

        log(str(e))

        log(traceback.format_exc())
