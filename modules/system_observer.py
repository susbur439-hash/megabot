import os
import re
import json


def run(data):
    project_root = "."

    system_map = {
        "files": [],
        "modules": [],
        "errors": [],
        "connections": [],
        "broken_links": [],
        "architecture_issues": []
    }

    skip_dirs = {"__pycache__", ".git", ".github", "venv", "env"}

    std_libs = {
        "os", "sys", "json", "re", "math", "random",
        "time", "datetime", "collections", "itertools",
        "subprocess", "threading", "asyncio", "logging",
        "importlib"
    }

    imports_map = {}

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

                # =========================
                # 🔗 УЛУЧШЕННЫЙ ПАРСИНГ ИМПОРТОВ
                # =========================
                imports = []

                # import x / import x.y
                matches = re.findall(r"import\s+([\w\.]+)", content)

                # from x import
                matches += re.findall(r"from\s+([\w\.]+)\s+import", content)

                for m in matches:
                    parts = m.split(".")
                    imports.append(parts[-1])  # берем имя модуля

                imports_map[rel_path] = imports

                # 🔗 run()
                has_run = "def run(" in content

                system_map["connections"].append({
                    "module": rel_path,
                    "has_run": has_run,
                    "imports": imports
                })

                # ⚠️ ошибки
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
    all_module_names = set(os.path.basename(f) for f in system_map["modules"])

    for module, imports in imports_map.items():
        for imp in imports:

            if imp in std_libs or len(imp) < 2:
                continue

            possible = imp + ".py"

            if possible not in all_module_names:
                system_map["broken_links"].append({
                    "module": module,
                    "missing": imp
                })

    # =========================
    # 🧠 ПОДКЛЮЧЕНИЕ АРХИТЕКТУРЫ
    # =========================
    blueprint = {}

    try:
        with open("megabot_architecture.json", "r", encoding="utf-8") as f:
            blueprint = json.load(f)
    except Exception:
        data.setdefault("log", []).append("⚠️ observer: blueprint не найден")

    required = blueprint.get("required_modules", [])

    # =========================
    # 🧠 ПРОВЕРКА АРХИТЕКТУРЫ
    # =========================

    # нормализуем имена файлов
    existing_names = set(os.path.basename(f) for f in system_map["modules"])

    # ❌ отсутствующие
    for req in required:
        if req not in existing_names:
            system_map["architecture_issues"].append({
                "type": "missing_module",
                "module": req
            })

    # 🧠 определяем используемые модули
    used_modules = set()

    for imports in imports_map.values():
        for imp in imports:
            used_modules.add(imp + ".py")

    # ⚠️ неиспользуемые
    for f in existing_names:
        if f not in required and f not in used_modules:
            system_map["architecture_issues"].append({
                "type": "unused_module",
                "module": f
            })

    # =========================
    # 📊 СТАТИСТИКА
    # =========================
    total = len(system_map["files"])
    modules = len(system_map["modules"])
    errors = len(system_map["errors"])
    broken = len(system_map["broken_links"])
    arch_issues = len(system_map["architecture_issues"])

    data["system_map"] = system_map

    # =========================
    # 📊 ЛОГ
    # =========================
    data.setdefault("log", []).append(
        f"👁 observer: files={total} modules={modules} errors={errors} broken_links={broken} arch_issues={arch_issues}"
    )

    # =========================
    # 🧠 УМНЫЙ ВЫВОД
    # =========================
    if arch_issues > 0:
        data["log"].append(f"⚠️ архитектура: проблем ({arch_issues})")

    if broken > 0:
        if broken > 20:
            data["log"].append(f"⚠️ связи: много ({broken})")
        else:
            data["log"].append(f"⚠️ связи: ({broken})")

    if errors > 0:
        data["log"].append(f"⚠️ ошибки: {errors}")

    if arch_issues == 0 and broken == 0 and errors == 0:
        data["log"].append("✅ система стабильна")

    data["log"].append("👁 observer executed")

    return data
