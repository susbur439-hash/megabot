import os
import re
import json


def run(data):
    print("👁 OBSERVER SCAN START")

    project_root = "."

    report = {
        "files": [],
        "modules": [],
        "critical": [],
        "warning": [],
        "info": [],
        "connections": [],
    }

    skip_dirs = {"__pycache__", ".git", ".github", "venv", "env"}

    std_libs = {
        "os", "sys", "json", "re", "math", "random",
        "time", "datetime", "collections", "itertools",
        "subprocess", "threading", "asyncio", "logging",
        "importlib", "traceback", "flask", "copy"
    }

    imports_map = {}
    usage_map = {}

    # =========================
    # 📁 СКАН ФАЙЛОВ
    # =========================
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, project_root)

            report["files"].append(rel_path)
            report["modules"].append(rel_path)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

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

                # wildcard import
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
    # 🔗 АНАЛИЗ СВЯЗЕЙ (FIXED)
    # =========================
    existing_files = set(report["modules"])

    # собираем имена файлов и папок
    file_names = {os.path.basename(f) for f in existing_files}
    dir_names = set(next(os.walk(project_root))[1])

    for module, imports in imports_map.items():
        for imp in imports:

            # пропускаем стандартные
            if imp in std_libs or len(imp) < 2:
                continue

            # если это папка (например modules) — это ОК
            if imp in dir_names:
                continue

            # проверка файла
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

                # CRITICAL только если реально внутренняя ошибка
                if module.startswith("modules/"):
                    report["critical"].append(issue)
                else:
                    report["warning"].append(issue)

    # =========================
    # 🧠 АРХИТЕКТУРА
    # =========================
    blueprint = {}

    try:
        with open("megabot_architecture.json", "r", encoding="utf-8") as f:
            blueprint = json.load(f)
    except Exception:
        report["info"].append({"type": "no_blueprint"})

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

    for mod in existing_names:
        if mod not in usage_map and mod not in {"main.py", "__init__.py"}:
            report["info"].append({
                "type": "unused_module",
                "module": mod
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
        "files": len(report["files"]),
        "modules": len(report["modules"]),
        "critical": len(report["critical"]),
        "warning": len(report["warning"]),
        "info": len(report["info"])
    }

    data["observer_report"] = {
        "stats": stats,
        "report": report
    }

    print(f"📊 files={stats['files']} modules={stats['modules']}")
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

    data.setdefault("log", []).append(
        f"👁 obs: C={stats['critical']} W={stats['warning']} I={stats['info']}"
    )

    for item in report["critical"][:2]:
        data["log"].append(f"❌ {item}")

    for item in report["warning"][:2]:
        data["log"].append(f"⚠️ {item}")

    print("✅ OBSERVER DONE")
    return data
