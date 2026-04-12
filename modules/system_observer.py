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
        "dead_modules": []  # 🔥 новые
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

    # =========================
    # 📁 СКАН ВСЕГО РЕПО
    # =========================
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for d in dirs:
            report["directories"].append(os.path.join(root, d))

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

                imports = []

                matches = re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE)
                matches += re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE)

                for m in matches:
                    base = m.split(".")[0]

                    if base not in imports:
                        imports.append(base)

                    usage_map.setdefault(base + ".py", []).append(rel_path)

                imports_map[rel_path] = imports

                has_run = "def run(" in content

                report["connections"].append({
                    "module": rel_path,
                    "has_run": has_run,
                    "imports": imports,
                    "used_by": []  # 🔥 добавим ниже
                })

                # ⚠️ wildcard
                if re.search(r"from\s+[\w\.]+\s+import\s+\*", content):
                    report["warning"].append({
                        "type": "wildcard_import",
                        "file": rel_path
                    })

                # ℹ️ нет run (но не для служебных файлов)
                if not has_run and not file.startswith("__"):
                    report["info"].append({
                        "type": "no_run_function",
                        "file": rel_path
                    })

                # ⚠️ пустой файл (НО НЕ __init__)
                if len(content.strip()) == 0 and file != "__init__.py":
                    report["warning"].append({
                        "type": "empty_file",
                        "file": rel_path
                    })

            except Exception as e:
                report["critical"].append({
                    "type": "file_read_error",
                    "file": rel_path,
                    "error": str(e)
                })

    # =========================
    # 🔗 АНАЛИЗ ИМПОРТОВ (УЛУЧШЕН)
    # =========================
    existing_files = set(report["modules"])
    file_names = {os.path.basename(f) for f in existing_files}

    # собираем папки ВСЕ (а не только корень)
    dir_names = set()
    for root, dirs, _ in os.walk(project_root):
        for d in dirs:
            dir_names.add(d)

    for module, imports in imports_map.items():
        for imp in imports:

            if imp in std_libs or len(imp) < 2:
                continue

            if imp in dir_names:
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
    # 🔗 USED BY (КТО ИСПОЛЬЗУЕТ)
    # =========================
    for module, imports in imports_map.items():
        for imp in imports:
            target = imp + ".py"

            for conn in report["connections"]:
                if conn["module"].endswith(target):
                    conn["used_by"].append(module)

    # =========================
    # 🧟 МЁРТВЫЕ МОДУЛИ
    # =========================
    for conn in report["connections"]:
        if (
            not conn["used_by"]
            and conn["module"] not in ["main.py"]
        ):
            report["dead_modules"].append(conn["module"])

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
        "python": len(report["files"]),
        "all": len(report["all_files"]),
        "dirs": len(report["directories"]),
        "critical": len(report["critical"]),
        "warning": len(report["warning"]),
        "info": len(report["info"]),
        "dead": len(report["dead_modules"])
    }

    data["observer_report"] = {
        "stats": stats,
        "report": report
    }

    # =========================
    # 🖥️ ВЫВОД
    # =========================
    print(f"📊 python={stats['python']} all={stats['all']} dirs={stats['dirs']}")
    print(f"🚨 critical={stats['critical']} ⚠️ warning={stats['warning']} ℹ️ info={stats['info']} 🧟 dead={stats['dead']}")

    print("\n=== OBSERVER REPORT ===")

    if report["critical"]:
        print(f"\n🚨 CRITICAL")
        for item in report["critical"][:5]:
            print("❌", item)

    if report["warning"]:
        print(f"\n⚠️ WARNING")
        for item in report["warning"][:5]:
            print("⚠️", item)

    if report["dead_modules"]:
        print(f"\n🧟 DEAD MODULES")
        for m in report["dead_modules"][:5]:
            print("💀", m)

    print("\n=== END ===")

    # =========================
    # 📋 ЛОГ
    # =========================
    data.setdefault("log", []).append(
        f"👁 obs: C={stats['critical']} W={stats['warning']} D={stats['dead']}"
    )

    print("✅ OBSERVER DONE")
    return data
