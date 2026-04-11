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
        "architecture_issues": [],
        "recommendations": []
    }

    skip_dirs = {"__pycache__", ".git", ".github", "venv", "env"}

    # стандарт + популярные библиотеки
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

                # import x / import x.y
                matches = re.findall(r"import\s+([\w\.]+)", content)

                # from x import y
                matches += re.findall(r"from\s+([\w\.]+)\s+import", content)

                for m in matches:
                    parts = m.split(".")
                    module_name = parts[0]  # ВАЖНО: берем корень

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
                    system_map["recommendations"].append(
                        f"{rel_path}: убрать import *"
                    )

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

            # игнор библиотек
            if imp in std_libs or len(imp) < 2:
                continue

            # ищем и в корне, и в modules/
            possible_files = {
                imp + ".py",
                f"modules/{imp}.py"
            }

            found = any(os.path.basename(p) in all_module_names for p in possible_files)

            if not found:
                system_map["broken_links"].append({
                    "module": module,
                    "missing": imp
                })
                system_map["recommendations"].append(
                    f"{module}: импорт '{imp}' не найден"
                )

    # =========================
    # 🧠 ПОДКЛЮЧЕНИЕ АРХИТЕКТУРЫ
    # =========================
    blueprint = {}

    try:
        with open("megabot_architecture.json", "r", encoding="utf-8") as f:
            blueprint = json.load(f)
    except Exception:
        data.setdefault("log", []).append("⚠️ observer: blueprint не найден")
        system_map["recommendations"].append("Добавить megabot_architecture.json")

    required = blueprint.get("required_modules", [])
    pipeline = blueprint.get("pipeline", [])

    existing_names = set(os.path.basename(f) for f in system_map["modules"])

    # =========================
    # ❌ ОТСУТСТВУЮЩИЕ МОДУЛИ
    # =========================
    for req in required:
        req_file = req if req.endswith(".py") else req + ".py"

        found = (
            req_file in existing_names or
            f"modules/{req_file}" in system_map["modules"]
        )

        if not found:
            system_map["architecture_issues"].append({
                "type": "missing_module",
                "module": req
            })
            system_map["recommendations"].append(
                f"Отсутствует обязательный модуль: {req}"
            )

    # =========================
    # ⚠️ НЕИСПОЛЬЗУЕМЫЕ МОДУЛИ
    # =========================
    for mod in existing_names:
        if mod not in usage_map and mod.replace(".py", "") not in required:
            # игнор служебных
            if mod in {"main.py", "__init__.py"}:
                continue

            system_map["architecture_issues"].append({
                "type": "unused_module",
                "module": mod
            })
            system_map["recommendations"].append(
                f"Модуль не используется: {mod}"
            )

    # =========================
    # 🔄 ПРОВЕРКА PIPELINE
    # =========================
    for step in pipeline:
        step_file = step if step.endswith(".py") else step + ".py"

        found = any(step in f for f in system_map["modules"])

        if not found:
            system_map["architecture_issues"].append({
                "type": "pipeline_missing",
                "step": step
            })
            system_map["recommendations"].append(
                f"Отсутствует этап pipeline: {step}"
            )

    # =========================
    # 📊 СТАТИСТИКА
    # =========================
    total = len(system_map["files"])
    modules = len(system_map["modules"])
    errors = len(system_map["errors"])
    broken = len(system_map["broken_links"])
    arch_issues = len(system_map["architecture_issues"])
    recs = len(system_map["recommendations"])

    data["system_map"] = system_map

    # =========================
    # 📊 ЛОГ
    # =========================
    data.setdefault("log", []).append(
        f"👁 observer: files={total} modules={modules} errors={errors} broken={broken} arch={arch_issues}"
    )

    # =========================
    # 🧠 ВЫВОД
    # =========================
    if arch_issues > 0:
        data["log"].append(f"⚠️ архитектура: {arch_issues} проблем")

    if broken > 0:
        data["log"].append(f"⚠️ связи: {broken}")

    if errors > 0:
        data["log"].append(f"⚠️ ошибки: {errors}")

    if recs > 0:
        data["log"].append(f"💡 рекомендаций: {recs}")

    if arch_issues == 0 and broken == 0 and errors == 0:
        data["log"].append("✅ система стабильна")

    data["log"].append("👁 observer executed")

    return data
