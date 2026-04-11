import os
import re


def run(data):
    project_root = "."

    system_map = {
        "files": [],
        "modules": [],
        "errors": [],
        "connections": []
    }

    skip_dirs = {"__pycache__", ".git", ".github", "venv", "env"}

    imports_map = {}

    # 📁 обход файлов
    for root, dirs, files in os.walk(project_root):

        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(root, file)
            system_map["files"].append(full_path)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                system_map["modules"].append(file)

                # 🔗 поиск импортов
                imports = []

                matches = re.findall(r"import (\w+)", content)
                matches += re.findall(r"from (\w+)", content)

                imports.extend(matches)
                imports_map[file] = imports

                # 🔗 проверка run
                has_run = "def run(" in content

                system_map["connections"].append({
                    "module": file,
                    "has_run": has_run,
                    "imports": imports
                })

                # ⚠️ простые ошибки
                if "import *" in content:
                    system_map["errors"].append({
                        "file": full_path,
                        "error": "wildcard import detected"
                    })

            except Exception as e:
                system_map["errors"].append({
                    "file": full_path,
                    "error": str(e)
                })

    # 🧠 АНАЛИЗ СВЯЗЕЙ
    broken_links = []

    all_modules = set(system_map["modules"])

    for module, imports in imports_map.items():
        for imp in imports:
            # если импорт похож на наш модуль, но его нет
            if imp.endswith(".py"):
                imp = imp.replace(".py", "")

            possible = imp + ".py"

            if possible not in all_modules:
                broken_links.append({
                    "module": module,
                    "missing": imp
                })

    # 📊 запись
    data["system_map"] = system_map
    data["system_map"]["broken_links"] = broken_links

    total = len(system_map["files"])
    modules = len(system_map["modules"])
    errors = len(system_map["errors"])
    broken = len(broken_links)

    # 📊 лог
    data.setdefault("log", []).append(
        f"👁 observer: files={total} modules={modules} errors={errors} broken_links={broken}"
    )

    # 🧠 интеллект
    if broken > 0:
        data["log"].append(f"⚠️ observer: найдено {broken} сломанных связей")
    elif errors > 0:
        data["log"].append(f"⚠️ observer: найдено {errors} ошибок")
    else:
        data["log"].append("✅ observer: система связана и стабильна")

    return data
