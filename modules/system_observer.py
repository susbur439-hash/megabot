import os
import re
import json


def run(data):
    print("👁 OBLIVION SCAN START")

    project_root = "."

    system_map = {
        "files": [],
        "modules": [],
        "errors": [],
        "connections": [],
        "broken_links": [],
        "architecture_issues": [],
        "recommendations": []
    }

    skip_dirs = {"__pycache__", ".git", ".github", "venv", "env"}

    std_libs = {
        "os", "sys", "json", "re", "math", "random",
        "time", "datetime", "collections", "itertools",
        "subprocess", "threading", "asyncio", "logging",
        "importlib", "traceback", "flask"
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

            system_map["files"].append(rel_path)
            system_map["modules"].append(rel_path)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                imports = []

                matches = re.findall(r"import\s+([\w\.]+)", content)
                matches += re.findall(r"from\s+([\w\.]+)\s+import", content)

                for m in matches:
                    module_name = m.split(".")[0]

                    if module_name not in imports:
                        imports.append(module_name)

                    usage_map.setdefault(module_name + ".py", []).append(rel_path)

                imports_map[rel_path] = imports

                has_run = "def run(" in content

                system_map["connections"].append({
                    "module": rel_path,
                    "has_run": has_run,
                    "imports": imports
                })

                if "import *" in content:
                    system_map["errors"].append({
                        "file": rel_path,
                        "error": "wildcard import detected"
                    })

            except Exception as e:
                system_map["errors"].append({
                    "file": rel_path,
                    "error": str(e)
                })

    # =========================
    # 🧠 АНАЛИЗ СВЯЗЕЙ
    # =========================
    existing_files = set(system_map["modules"])

    for module, imports in imports_map.items():
        for imp in imports:
            if imp in std_libs or len(imp) < 2:
                continue

            found = any(
                imp + ".py" in f or f.endswith(f"/{imp}.py")
                for f in existing_files
            )

            if not found:
                system_map["broken_links"].append({
                    "module": module,
                    "missing": imp
                })

    # =========================
    # 🧠 АРХИТЕКТУРА
    # =========================
    blueprint = {}

    try:
        with open("megabot_architecture.json", "r", encoding="utf-8") as f:
            blueprint = json.load(f)
    except Exception:
        system_map["recommendations"].append("Добавить megabot_architecture.json")

    required = blueprint.get("required_modules", [])
    pipeline = blueprint.get("pipeline", [])

    existing_names = set(os.path.basename(f) for f in existing_files)

    # отсутствующие модули
    for req in required:
        req_file = req if req.endswith(".py") else req + ".py"

        if req_file not in existing_names:
            system_map["architecture_issues"].append({
                "type": "missing_module",
                "module": req
            })

    # неиспользуемые
    for mod in existing_names:
        if mod not in usage_map and mod not in {"main.py", "__init__.py"}:
            system_map["architecture_issues"].append({
                "type": "unused_module",
                "module": mod
            })

    # pipeline
    for step in pipeline:
        if not any(step in f for f in existing_files):
            system_map["architecture_issues"].append({
                "type": "pipeline_missing",
                "step": step
            })

    # =========================
    # 📊 СТАТИСТИКА
    # =========================
    errors = len(system_map["errors"])
    broken = len(system_map["broken_links"])
    arch = len(system_map["architecture_issues"])

    data["system_map"] = system_map

    print(f"📊 files={len(system_map['files'])} modules={len(system_map['modules'])}")
    print(f"❌ errors={errors} broken={broken} arch={arch}")

    # =========================
    # ❌ ЛОМАЕМ WORKFLOW ЕСЛИ ПРОБЛЕМЫ
    # =========================
    if errors > 0 or broken > 0 or arch > 0:
        print("\n🚨 OBLIVION FOUND PROBLEMS:")

        for e in system_map["errors"][:5]:
            print("ERROR:", e)

        for b in system_map["broken_links"][:5]:
            print("BROKEN:", b)

        for a in system_map["architecture_issues"][:5]:
            print("ARCH:", a)

        raise Exception("OBLIVION FAILED")

    print("✅ OBLIVION OK")
    return data
