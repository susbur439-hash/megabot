import os
import re
import json


def run(data):
    print("👁 OBSERVER SCAN START")

    project_root = "."

    report = {
        "files": [],
        "all_files": [],
        "non_python_files": [],
        "directories": [],
        "modules": [],
        "critical": [],
        "warning": [],
        "info": [],
        "connections": [],
    }

    skip_dirs = {"__pycache__", ".git", "venv", "env"}

    std_libs = {
        "os", "sys", "json", "re", "math", "random",
        "time", "datetime", "collections", "itertools",
        "subprocess", "threading", "asyncio", "logging",
        "importlib", "traceback", "flask", "copy"
    }

    imports_map = {}
    usage_map = {}
    all_dirs = set()

    # =========================
    # 📁 СКАН ВСЕГО РЕПО
    # =========================
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for d in dirs:
            full_dir = os.path.join(root, d)
            rel_dir = os.path.relpath(full_dir, project_root)
            report["directories"].append(rel_dir)
            all_dirs.add(d)

        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, project_root)

            report["all_files"].append(rel_path)

            if not file.endswith(".py"):
                report["non_python_files"].append(rel_path)
                continue

            report["files"].append(rel_path)
            report["modules"].append(rel_path)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 🔥 пустой файл
                if not content.strip():
                    report["warning"].append({
                        "type": "empty_file",
                        "file": rel_path
                    })

                imports = []

                matches = re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE)
                matches += re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE)

                for m in matches:
                    base_module = m.split(".")[0]

                    if base_module not in imports:
                        imports.append(base_module)

                    usage_map.setdefault(base_module + ".py", []).append(rel_path)

                imports_map[rel_path] = imports

                has_run = "def run(" in content

                report["connections"].append({
                    "module": rel_path,
                    "has_run": has_run,
                    "imports": imports
                })

                if re.search(r"from\s+[\w\.]+\s+import\s+\*", content):
                    report["warning"].append({
                        "type": "wildcard_import",
                        "file": rel_path
                    })

                if not has_run:
                    report["info"].append({
                        "type": "no_run_function",
                        "file": rel_path
                    })

            except Exception as e:
                report["critical"].append({
                    "type": "file_read_error",
                    "file": rel_path,
                    "error": str(e)
                })

    # =========================
    # 🔗 АНАЛИЗ ИМПОРТОВ
    # =========================
    existing_files = set(report["modules"])
    file_names = {os.path.basename(f) for f in existing_files}

    for module, imports in imports_map.items():
        for imp in imports:

            if imp in std_libs or len(imp) < 2:
                continue

            # если это папка (например modules)
            if imp in all_dirs:
                continue

            found = (
                f"{imp}.py" in file_names or
                any(f.endswith(f"/{imp}.py") for f in existing_files)
            )

            if not found:
                issue = {
                    "type": "missing_import",
                    "module": module,
                    "missing": imp
                }

                if module.startswith("modules/"):
                    report["critical"].append(issue)
                else:
                    report["warning"].append(issue)

    # =========================
    # 🧠 ПОИСК "СИРОТ" (ВАЖНО)
    # =========================
    for module in report["modules"]:
        name = os.path.basename(module)

        if name not in usage_map and module != "main.py":
            report["warning"].append({
                "type": "orphan_module",
                "module": module
            })

    # =========================
    # 🧠 АРХИТЕКТУРА
    # =========================
    blueprint = {}

    try:
        with open("megabot_architecture.json", "r", encoding="utf-8") as f:
            blueprint = json.load(f)
    except Exception:
        report["critical"].append({"type": "no_architecture_file"})

    required = blueprint.get("required_modules", [])
    pipeline = blueprint.get("core_loop", [])

    existing_names = set(os.path.basename(f) for f in existing_files)

    for req in required:
        req_file = req if req.endswith(".py") else req + ".py"

        if req_file not in existing_names:
            report["warning"].append({
                "type": "missing_module",
                "module": req
            })

    for step in pipeline:
        if not any(step in f for f in existing_files):
            report["warning"].append({
                "type": "pipeline_missing",
                "step": step
            })

    # =========================
    # 📊 СТАТИСТИКА
    # =========================
    stats = {
        "python_files": len(report["files"]),
        "all_files": len(report["all_files"]),
        "non_python": len(report["non_python_files"]),
        "dirs": len(report["directories"]),
        "critical": len(report["critical"]),
        "warning": len(report["warning"]),
        "info": len(report["info"])
    }

    data["observer_report"] = {
        "stats": stats,
        "report": report
    }

    # =========================
    # 🖥️ ВЫВОД
    # =========================
    print(f"📊 python={stats['python_files']} all={stats['all_files']} dirs={stats['dirs']}")
    print(f"🚨 critical={stats['critical']} ⚠️ warning={stats['warning']} ℹ️ info={stats['info']}")

    print("\n=== OBSERVER REPORT ===")

    if report["critical"]:
        print(f"\n🚨 CRITICAL ({len(report['critical'])})")
        for item in report["critical"][:5]:
            print("❌", item)

    if report["warning"]:
        print(f"\n⚠️ WARNING ({len(report['warning'])})")
        for item in report["warning"][:5]:
            print("⚠️", item)

    if report["info"]:
        print(f"\nℹ️ INFO ({len(report['info'])})")
        for item in report["info"][:5]:
            print("ℹ️", item)

    print("\n=== END ===")

    # =========================
    # 📋 ЛОГ
    # =========================
    data.setdefault("log", []).append(
        f"👁 obs: C={stats['critical']} W={stats['warning']} ALL={stats['all_files']}"
    )

    for item in report["critical"][:2]:
        data["log"].append(f"❌ {item}")

    for item in report["warning"][:2]:
        data["log"].append(f"⚠️ {item}")

    print("✅ OBSERVER DONE")
    return data
