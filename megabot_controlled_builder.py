# =========================================================
# 🧠 MEGABOT CONTROLLED BUILDER MAX
# =========================================================
# Один главный файл Megabot
#
# Функции:
# - сканирование проекта
# - контроль архитектуры
# - создание недостающих файлов
# - repair system
# - self-test
# - anti-loop
# - memory
# - github-ready
#
# Запуск:
# python megabot_controlled_builder.py
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
        return {
            "cycles": 0,
            "history": [],
            "fixed": [],
            "created": []
        }

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return {
            "cycles": 0,
            "history": [],
            "fixed": [],
            "created": []
        }


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
# 🔍 SCAN PROJECT
# =========================================================

def scan_project():

    project = {
        "files": [],
        "modules": [],
        "missing": [],
    }

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
# 🧠 ANALYZE ARCHITECTURE
# =========================================================

def analyze_architecture(project):

    missing = []

    # core
    for file in TARGET_ARCHITECTURE["core"]:

        if not os.path.exists(file):
            missing.append(file)

    # modules
    for module in TARGET_ARCHITECTURE["modules"]:

        path = os.path.join(MODULES_DIR, module)

        if not os.path.exists(path):
            missing.append(path)

    return missing


# =========================================================
# 🏗 DEFAULT MODULE TEMPLATE
# =========================================================

def build_module_template(name):

    pure = name.replace(".py", "")

    return f'''# =========================================================
# 🧠 {pure.upper()}
# =========================================================

def run(data):

    if not isinstance(data, dict):
        data = {{}}

    data.setdefault("log", [])

    data["log"].append("⚙️ {pure} running")

    return data
'''


# =========================================================
# 🏗 CREATE FILE
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
# 🔧 AUTOFIX IMPORTS
# =========================================================

def repair_python_file(path):

    try:

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        changed = False

        # fix tabs
        if "\t" in content:
            content = content.replace("\t", "    ")
            changed = True

        # fix empty files
        if len(content.strip()) == 0:

            content = build_module_template(
                os.path.basename(path)
            )

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
# 🧪 TEST FILE
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
# 🧪 RUN TESTS
# =========================================================

def run_tests(project):

    failed = []

    for file in project["files"]:

        if not file.endswith(".py"):
            continue

        ok, err = test_python_file(file)

        if not ok:

            failed.append({
                "file": file,
                "error": err
            })

            log(f"❌ TEST FAIL: {file}")
            log(f"   ↳ {err}")

        else:

            log(f"✅ TEST OK: {file}")

    return failed


# =========================================================
# 🧠 BUILD LOOP
# =========================================================

def build_cycle():

    memory = load_memory()

    log("")
    log("=================================================")
    log("🧠 MEGABOT CONTROLLED BUILDER")
    log("=================================================")

    # =====================================================
    # 🔍 SCAN
    # =====================================================

    project = scan_project()

    log(f"📦 FILES: {len(project['files'])}")
    log(f"🧩 MODULES: {len(project['modules'])}")

    # =====================================================
    # 🧠 ANALYZE
    # =====================================================

    missing = analyze_architecture(project)

    if missing:

        log("")
        log("🚨 MISSING FILES:")

        for m in missing:
            log(f" - {m}")

    else:

        log("✅ ARCHITECTURE COMPLETE")

    # =====================================================
    # 🏗 CREATE MISSING
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

                repaired = repair_python_file(file)

                if repaired:
                    memory["fixed"].append(file)

    # =====================================================
    # 🧪 TESTS
    # =====================================================

    failed = []

    if ENABLE_TESTS:

        log("")
        log("🧪 RUNNING TESTS")

        failed = run_tests(scan_project())

    # =====================================================
    # 📊 REPORT
    # =====================================================

    report = {
        "timestamp": time.time(),
        "missing": missing,
        "failed": failed,
        "logs": LOGS[-500:]
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # =====================================================
    # 🧠 MEMORY UPDATE
    # =====================================================

    memory["cycles"] += 1

    memory["history"].append({
        "time": time.time(),
        "missing": len(missing),
        "failed": len(failed)
    })

    save_memory(memory)

    # =====================================================
    # 📊 FINAL
    # =====================================================

    log("")
    log("=================================================")
    log("📊 BUILD FINISHED")
    log("=================================================")

    log(f"🧠 cycles: {memory['cycles']}")
    log(f"🧩 created: {len(memory['created'])}")
    log(f"🔧 fixed: {len(memory['fixed'])}")
    log(f"❌ failed tests: {len(failed)}")

    log("")
    log("✅ DONE")


# =========================================================
# ▶️ MAIN
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
