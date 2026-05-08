# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX
# =========================================================

import os
import json
import time
import traceback
from pathlib import Path

# =========================================================
# ⚙ CONFIG
# =========================================================

ROOT_DIR = "."
MODULES_DIR = "modules"

MEMORY_FILE = "builder_memory.json"
REPORT_FILE = "builder_report.json"

MAX_CYCLES = 1

ENABLE_AUTOFIX = True
ENABLE_FILE_CREATION = True
ENABLE_TESTS = True
ENABLE_CLEANUP = True

# 🆕 SAFETY MODE (ВАЖНО)
ENABLE_SAFE_DELETE = True

# =========================================================
# 🧠 TARGET ARCHITECTURE
# =========================================================

TARGET_ARCHITECTURE = {
    "core": [
        "main.py",
        "megabot_controlled_builder.py",
    ],

    "modules": [
        "task_interpreter.py",
        "planner.py",
        "decision.py",
        "execution.py",
        "evaluation.py",
        "memory.py",
        "learning.py",
        "control_layer.py",
    ]
}

# =========================================================
# 🧠 MEMORY
# =========================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"cycles": 0, "history": [], "fixed": [], "created": [], "deleted": []}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"cycles": 0, "history": [], "fixed": [], "created": [], "deleted": []}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

# =========================================================
# 📋 LOGGER
# =========================================================

LOGS = []

def log(message):
    print(message)
    LOGS.append(message)

# =========================================================
# 🔍 SCAN
# =========================================================

def scan_project():
    project = {"files": [], "modules": [], "missing": []}

    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root:
            continue

        for file in files:
            path = os.path.join(root, file)
            project["files"].append(path)

            if root.endswith("modules"):
                project["modules"].append(file)

    return project

# =========================================================
# 🧠 ARCHITECTURE ANALYSIS
# =========================================================

def analyze_architecture(project):
    missing = []

    for file in TARGET_ARCHITECTURE["core"]:
        if not os.path.exists(file):
            missing.append(file)

    for module in TARGET_ARCHITECTURE["modules"]:
        path = os.path.join(MODULES_DIR, module)
        if not os.path.exists(path):
            missing.append(path)

    return missing

# =========================================================
# 🧱 ARCHITECTURE LOCK (NEW)
# =========================================================

def is_core_module(module_name):
    return module_name in TARGET_ARCHITECTURE["modules"]

# =========================================================
# 🧠 SMART USAGE SCORE (NEW)
# =========================================================

def usage_score(module_name, project):

    score = 0
    name = module_name.replace(".py", "")

    for file in project["files"]:

        if not file.endswith(".py"):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()

            if name in content:
                score += 2

            if f"import {name}" in content:
                score += 3

            if f"from {name}" in content:
                score += 3

            if f"{name}.run" in content:
                score += 4

        except:
            continue

    return score

# =========================================================
# 🗑 FIND UNUSED (UPGRADED)
# =========================================================

def find_unused_modules(project):

    unused = []

    for module in project["modules"]:

        full_path = os.path.join(MODULES_DIR, module)

        # 🛑 защита ядра
        if is_core_module(module):
            continue

        score = usage_score(module, project)

        # 🧠 только реально мёртвые
        if score == 0:
            unused.append((full_path, score))

    return unused

# =========================================================
# 🗑 SAFE DELETE
# =========================================================

def delete_file(path):

    if not ENABLE_SAFE_DELETE:
        return False

    try:
        if os.path.exists(path):
            os.remove(path)
            log(f"🗑 DELETED UNUSED: {path}")
            return True
    except Exception as e:
        log(f"❌ DELETE ERROR: {path} | {e}")

    return False

# =========================================================
# 🏗 TEMPLATE
# =========================================================

def build_module_template(name):

    pure = name.replace(".py", "")

    return f"""# =========================================================
# 🧠 {pure.upper()}
# =========================================================

def run(data):

    if not isinstance(data, dict):
        data = {{}}

    data.setdefault("log", [])

    data["log"].append("⚙️ {pure} running")

    return data
"""

# =========================================================
# 🏗 CREATE
# =========================================================

def create_missing_file(path):

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        filename = os.path.basename(path)
        content = build_module_template(filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        log(f"🧩 CREATED: {path}")
        return True

    except Exception as e:
        log(f"❌ CREATE ERROR: {path} | {e}")
        return False

# =========================================================
# 🔧 REPAIR
# =========================================================

def repair_python_file(path):

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        changed = False

        if "\t" in content:
            content = content.replace("\t", "    ")
            changed = True

        if len(content.strip()) == 0:
            content = build_module_template(os.path.basename(path))
            changed = True

        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            log(f"🔧 REPAIRED: {path}")
            return True

    except Exception as e:
        log(f"❌ REPAIR ERROR: {path} | {e}")

    return False

# =========================================================
# 🧪 TEST
# =========================================================

def test_python_file(path):

    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        compile(source, path, "exec")
        return True, None

    except Exception as e:
        return False, str(e)

# =========================================================
# 🧠 BUILD CYCLE
# =========================================================

def build_cycle():

    memory = load_memory()

    log("\n=================================================")
    log("🧠 MEGABOT CONTROLLED BUILDER")
    log("=================================================")

    project = scan_project()

    log(f"📦 FILES: {len(project['files'])}")
    log(f"🧩 MODULES: {len(project['modules'])}")

    missing = analyze_architecture(project)

    if missing:
        log("\n🚨 MISSING FILES:")
        for m in missing:
            log(f" - {m}")
    else:
        log("✅ ARCHITECTURE COMPLETE")

    # =====================================================
    # 🏗 CREATE
    # =====================================================

    if ENABLE_FILE_CREATION:
        for path in missing:
            if create_missing_file(path):
                memory["created"].append(path)

    # =====================================================
    # 🔧 REPAIR
    # =====================================================

    if ENABLE_AUTOFIX:
        for file in project["files"]:
            if file.endswith(".py"):
                if repair_python_file(file):
                    memory["fixed"].append(file)

    # =====================================================
    # 🗑 CLEANUP (SAFE)
    # =====================================================

    if ENABLE_CLEANUP:

        unused = find_unused_modules(project)

        if unused:
            log("\n🗑 UNUSED MODULES (SAFE SCORE 0):")

            for path, score in unused:
                log(f" - {path} | score={score}")

                if delete_file(path):
                    memory["deleted"].append(path)

    # =====================================================
    # 🧪 TESTS
    # =====================================================

    failed = []

    if ENABLE_TESTS:

        log("\n🧪 RUNNING TESTS")

        for file in project["files"]:
            if file.endswith(".py"):
                ok, err = test_python_file(file)

                if not ok:
                    failed.append({"file": file, "error": err})
                    log(f"❌ FAIL: {file}")
                else:
                    log(f"✅ OK: {file}")

    # =====================================================
    # 📊 MEMORY
    # =====================================================

    memory["cycles"] += 1

    memory["history"].append({
        "time": time.time(),
        "missing": len(missing),
        "failed": len(failed),
        "deleted": len(memory.get("deleted", []))
    })

    save_memory(memory)

    # =====================================================
    # 📊 FINAL
    # =====================================================

    log("\n=================================================")
    log("📊 BUILD FINISHED")
    log("=================================================")

    log(f"🧠 cycles: {memory['cycles']}")
    log(f"🧩 created: {len(memory['created'])}")
    log(f"🔧 fixed: {len(memory['fixed'])}")
    log(f"🗑 deleted: {len(memory.get('deleted', []))}")
    log(f"❌ failed: {len(failed)}")

    log("\n✅ DONE")

# =========================================================
# ▶️ MAIN
# =========================================================

if __name__ == "__main__":

    try:
        for _ in range(MAX_CYCLES):
            build_cycle()

    except Exception as e:
        log("❌ FATAL ERROR")
        log(str(e))
        log(traceback.format_exc())
