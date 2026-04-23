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
        "dead_modules": []
    }

    skip_dirs = {"__pycache__", ".git", "venv", "env"}

    std_libs = {
        "os", "sys", "json", "re", "math", "random",
        "time", "datetime", "collections", "itertools",
        "subprocess", "threading", "asyncio", "logging",
        "importlib", "traceback", "flask", "copy"
    }

    imports_map = {}

    # =========================
    # 📁 SCAN PROJECT
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

                imports = set()

                matches = re.findall(r"^\s*import\s+([\w\.]+)", content, re.MULTILINE)
                matches += re.findall(r"^\s*from\s+([\w\.]+)\s+import", content, re.MULTILINE)

                for m in matches:
                    base = m.split(".")[0]
                    if base:
                        imports.add(base)

                imports_map[rel_path] = list(imports)

                has_run = "def run(" in content

                report["connections"].append({
                    "module": rel_path,
                    "has_run": has_run,
                    "imports": list(imports),
                    "used_by": []
                })

                if re.search(r"from\s+[\w\.]+\s+import\s+\*", content):
                    report["warning"].append({
                        "type": "wildcard_import",
                        "file": rel_path
                    })

                if not has_run and file != "__init__.py":
                    report["info"].append({
                        "type": "no_run_function",
                        "file": rel_path
                    })

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
    # 🔗 IMPORT ANALYSIS (FIXED)
    # =========================
    existing_files = set(report["modules"])
    file_names = {os.path.basename(f) for f in existing_files}

    dir_names = set()
    for root, dirs, _ in os.walk(project_root):
        for d in dirs:
            dir_names.add(d)

    for module, imports in imports_map.items():
        for imp in imports:

            if imp in std_libs:
                continue

            if imp in dir_names:
                continue

            if len(imp) < 2:
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
    # 🔗 USED BY FIXED
    # =========================
    for conn in report["connections"]:
        module_name = os.path.basename(conn["module"])

        for other, imports in imports_map.items():
            if module_name.replace(".py", "") in imports:
                conn["used_by"].append(other)

    # =========================
    # 🧟 DEAD MODULES (FIXED)
    # =========================
    for conn in report["connections"]:
        file = conn["module"]

        if file in ["main.py"]:
            continue

        if file.startswith("modules/__init__"):
            continue

        if not conn["used_by"] and not conn["has_run"]:
            report["dead_modules"].append(file)

    # =========================
    # 📊 STATS
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

    print(f"📊 python={stats['python']} all={stats['all']} dirs={stats['dirs']}")
    print(f"🚨 critical={stats['critical']} ⚠️ warning={stats['warning']} ℹ️ info={stats['info']} 🧟 dead={stats['dead']}")

    print("\n=== OBSERVER REPORT ===")

    if report["critical"]:
        print("\n🚨 CRITICAL")
        for item in report["critical"][:5]:
            print("❌", item)

    if report["warning"]:
        print("\n⚠️ WARNING")
        for item in report["warning"][:5]:
            print("⚠️", item)

    if report["dead_modules"]:
        print("\n🧟 DEAD MODULES")
        for m in report["dead_modules"][:5]:
            print("💀", m)

    print("\n=== END ===")

    data.setdefault("log", []).append(
        f"👁 obs: C={stats['critical']} W={stats['warning']} D={stats['dead']}"
    )

    print("✅ OBSERVER DONE")
    return data
