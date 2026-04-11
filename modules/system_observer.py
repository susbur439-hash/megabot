import os
import re


def run(data):
    project_root = "."

    system_map = {
        "files": [],
        "modules": [],
        "errors": [],
        "connections": [],
        "broken_links": []
    }

    skip_dirs = {"__pycache__", ".git", ".github", "venv", "env"}

    # стандартные библиотеки (игнор)
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

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                system_map["modules"].append(rel_path)

                # =========================
                # 🔗 ПОИСК ИМПОРТОВ
                # =========================
                imports = []

                matches = re.findall(r"import (\w+)", content)
                matches += re.findall(r"from (\w+)", content)

                imports.extend(matches)
                imports_map[rel_path] = imports

                # =========================
                # 🔗 ПРОВЕРКА run()
                # =========================
                has_run = "def run(" in content

                system_map["connections"].append({
                    "module": rel_path,
                    "has_run": has_run,
                    "imports": imports
                })

                # =========================
                # ⚠️ ПРОСТЫЕ ОШИБКИ
                # =========================
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
    all_modules = set(system_map["modules"])

    for module, imports in imports_map.items():
        for imp in imports:

            # игнор стандартных библиотек
            if imp in std_libs:
                continue

            # игнор коротких/подозрительных
            if len(imp) < 2:
                continue

            # пробуем найти файл
            possible_paths = [
                f"{imp}.py",
                f"modules/{imp}.py",
                f"./{imp}.py"
            ]

            found = any(p in all_modules for p in possible_paths)

            if not found:
                system_map["broken_links"].append({
                    "module": module,
                    "missing": imp
                })

    # =========================
    # 📊 СТАТИСТИКА
    # =========================
    total = len(system_map["files"])
    modules = len(system_map["modules"])
    errors = len(system_map["errors"])
    broken = len(system_map["broken_links"])

    data["system_map"] = system_map

    # =========================
    # 📊 ЛОГ
    # =========================
    data.setdefault("log", []).append(
        f"👁 observer: files={total} modules={modules} errors={errors} broken_links={broken}"
    )

    # =========================
    # 🧠 УМНЫЙ ВЫВОД
    # =========================
    if broken > 0:
        if broken > 20:
            data["log"].append(f"⚠️ observer: много связей отсутствует ({broken})")
        else:
            data["log"].append(f"⚠️ observer: найдено {broken} проблемных связей")

    elif errors > 0:
        data["log"].append(f"⚠️ observer: найдено {errors} ошибок")

    else:
        data["log"].append("✅ observer: система связана и стабильна")

    data["log"].append("👁 observer executed")

    return data
