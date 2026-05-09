# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX v4
# 🛡 CORE SAFE + AUTO REPAIR + QUARANTINE
# =========================================================

import os
import json
import traceback
import shutil
import importlib.util

ROOT_DIR = "."
MODULES_DIR = "modules"

MEMORY_FILE = "builder_memory.json"
REPORT_FILE = "builder_report.json"

QUARANTINE_DIR = "quarantine"

MAX_CYCLES = 1

ENABLE_CLEANUP = True
ENABLE_SAFE_DELETE = False
ENABLE_QUARANTINE = True

ENABLE_AUTOREPAIR = True
ENABLE_RUNTIME_TEST = True

MIN_LIVE_CYCLES_BEFORE_DELETE = 2

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
]

# =========================================================
# 🧠 MEMORY
# =========================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {
            "cycles": 0,
            "module_age": {},
            "deleted": [],
            "repaired": [],
            "runtime_failed": []
        }

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return {
            "cycles": 0,
            "module_age": {},
            "deleted": [],
            "repaired": [],
            "runtime_failed": []
        }


def save_memory(m):

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)

# =========================================================
# 📋 LOG
# =========================================================

LOGS = []

def log(x):

    print(x)
    LOGS.append(str(x))

# =========================================================
# 🔍 SCAN
# =========================================================

def scan():

    files = []
    modules = []

    for r, d, f in os.walk(ROOT_DIR):

        if ".git" in r:
            continue

        if QUARANTINE_DIR in r:
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

                if f"import {name}" in c:
                    deps[m].add(file)

                if f"from {name}" in c:
                    deps[m].add(file)

                if f"{name}." in c:
                    deps[m].add(file)

        except:
            continue

    return deps

# =========================================================
# 🧠 SCORE
# =========================================================

def module_score(module, deps):

    score = 0

    if module in deps:
        score += len(deps[module]) * 3

    if len(deps.get(module, [])) > 0:
        score += 5

    return score

# =========================================================
# 🧠 DELETE RULE
# =========================================================

def should_delete(module, score, deps, age):

    if is_core(module):
        return False

    if score > 0:
        return False

    if len(deps.get(module, [])) > 0:
        return False

    if age < MIN_LIVE_CYCLES_BEFORE_DELETE:
        return False

    return True

# =========================================================
# 🧠 QUARANTINE
# =========================================================

def quarantine_file(path):

    try:

        os.makedirs(QUARANTINE_DIR, exist_ok=True)

        filename = os.path.basename(path)

        dst = os.path.join(QUARANTINE_DIR, filename)

        shutil.move(path, dst)

        log(f"📦 QUARANTINED: {path}")

        return True

    except Exception as e:

        log(f"❌ QUARANTINE ERROR: {e}")

        return False

# =========================================================
# 🏗 TEMPLATE
# =========================================================

def build_template(module_name):

    pure = module_name.replace(".py", "")

    return f'''# =========================================================
# 🧠 AUTO-REPAIRED MODULE: {pure}
# =========================================================

def run(data=None):

    if data is None:
        data = {{}}

    if not isinstance(data, dict):
        data = {{}}

    data.setdefault("log", [])

    data["log"].append("⚙️ {pure} executed")

    return data
'''

# =========================================================
# 🔧 REPAIR MODULE
# =========================================================

def repair_module(path, memory):

    try:

        filename = os.path.basename(path)

        backup_dir = "repair_backups"

        os.makedirs(backup_dir, exist_ok=True)

        backup_path = os.path.join(backup_dir, filename)

        shutil.copy(path, backup_path)

        with open(path, "w", encoding="utf-8") as f:
            f.write(build_template(filename))

        memory["repaired"].append(path)

        log(f"🔧 REPAIRED MODULE: {path}")

        return True

    except Exception as e:

        log(f"❌ REPAIR FAILED: {path} | {e}")

        return False

# =========================================================
# 🧪 SYNTAX TEST
# =========================================================

def syntax_test(path):

    try:

        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        compile(source, path, "exec")

        return True, None

    except Exception as e:

        return False, str(e)

# =========================================================
# 🧪 RUNTIME TEST
# =========================================================

def runtime_test(path):

    try:

        module_name = os.path.basename(path).replace(".py", "")

        spec = importlib.util.spec_from_file_location(
            module_name,
            path
        )

        mod = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(mod)

        if hasattr(mod, "run"):

            result = mod.run({})

            return True, result

        return False, "NO RUN FUNCTION"

    except Exception as e:

        return False, str(e)

# =========================================================
# 🧠 MAIN
# =========================================================

def build_cycle():

    memory = load_memory()

    files, modules = scan()

    deps = build_dependencies(files, modules)

    log("")
    log("=================================================")
    log("🧠 MEGABOT BUILDER v4")
    log("=================================================")

    log(f"📦 FILES: {len(files)}")
    log(f"🧩 MODULES: {len(modules)}")

    # =====================================================
    # 🧪 MODULE VALIDATION
    # =====================================================

    log("")
    log("🧪 VALIDATING MODULES")

    for module in modules:

        path = os.path.join(MODULES_DIR, module)

        ok, err = syntax_test(path)

        if not ok:

            log(f"❌ SYNTAX FAIL: {path}")
            log(f"   ↳ {err}")

            if ENABLE_AUTOREPAIR:
                repair_module(path, memory)

            continue

        log(f"✅ SYNTAX OK: {path}")

        if ENABLE_RUNTIME_TEST:

            ok_runtime, runtime_err = runtime_test(path)

            if not ok_runtime:

                log(f"⚠️ RUNTIME FAIL: {path}")
                log(f"   ↳ {runtime_err}")

                memory["runtime_failed"].append(path)

            else:

                log(f"🚀 RUNTIME OK: {path}")

    # =====================================================
    # 🗑 CLEANUP
    # =====================================================

    if ENABLE_CLEANUP:

        log("")
        log("🗑 CLEANUP CHECK")

        for m in modules:

            path = os.path.join(MODULES_DIR, m)

            score = module_score(m, deps)

            age = memory["module_age"].get(m, 0)

            if should_delete(m, score, deps, age):

                log(f"⚠️ UNUSED: {path}")

                if ENABLE_QUARANTINE:

                    if quarantine_file(path):
                        memory["deleted"].append(path)

                elif ENABLE_SAFE_DELETE:

                    try:
                        os.remove(path)

                        memory["deleted"].append(path)

                        log(f"🗑 DELETED: {path}")

                    except Exception as e:
                        log(f"❌ DELETE ERROR: {e}")

            else:

                memory["module_age"][m] = age + 1

    # =====================================================
    # 📊 REPORT
    # =====================================================

    report = {
        "cycles": memory["cycles"] + 1,
        "deleted": len(memory["deleted"]),
        "repaired": len(memory["repaired"]),
        "runtime_failed": len(memory["runtime_failed"]),
        "logs": LOGS[-300:]
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # =====================================================
    # 💾 SAVE MEMORY
    # =====================================================

    memory["cycles"] += 1

    save_memory(memory)

    # =====================================================
    # 📊 FINAL
    # =====================================================

    log("")
    log("=================================================")
    log("📊 BUILD FINISHED")
    log("=================================================")

    log(f"🧠 cycles: {memory['cycles']}")
    log(f"🔧 repaired: {len(memory['repaired'])}")
    log(f"⚠️ runtime failed: {len(memory['runtime_failed'])}")
    log(f"🗑 quarantined: {len(memory['deleted'])}")

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

        log("❌ FATAL")

        log(str(e))

        log(traceback.format_exc())
