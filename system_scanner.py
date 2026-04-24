import os
import ast
import json

ROOT = "."

# =========================
# 📦 СКАН ФАЙЛОВ
# =========================
def scan_py_files():
    files = []
    for root, _, fs in os.walk(ROOT):
        for f in fs:
            if f.endswith(".py"):
                files.append(os.path.join(root, f))
    return files


# =========================
# 🔍 ИЗВЛЕЧЕНИЕ IMPORTS
# =========================
def extract_imports(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)

        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    except Exception as e:
        return [f"ERROR:{e}"]


# =========================
# 🧠 СТРОИМ КАРТУ СИСТЕМЫ
# =========================
def build_system_map():
    files = scan_py_files()

    system_map = {
        "total_files": len(files),
        "modules": {},
        "broken_imports": [],
        "orphan_files": [],
        "core_candidates": [],
    }

    all_imports = {}

    for f in files:
        imports = extract_imports(f)
        all_imports[f] = imports
        system_map["modules"][f] = imports

        for imp in imports:
            if "ERROR" in imp:
                system_map["broken_imports"].append((f, imp))

    # =========================
    # 🧩 поиск "сирот"
    # =========================
    used = set()
    for deps in all_imports.values():
        for d in deps:
            used.add(d.split(".")[0])

    for f in files:
        name = os.path.basename(f).replace(".py", "")
        if name not in str(all_imports):
            system_map["orphan_files"].append(f)

    # =========================
    # 🧠 поиск ядра системы
    # =========================
    core_keywords = [
        "engine",
        "brain",
        "control",
        "director",
        "decision",
        "planning",
        "observer",
        "state"
    ]

    for f in files:
        low = f.lower()
        if any(k in low for k in core_keywords):
            system_map["core_candidates"].append(f)

    return system_map


# =========================
# 🚀 ЗАПУСК
# =========================
if __name__ == "__main__":
    result = build_system_map()

    print("\n🧠 SYSTEM SCAN COMPLETE")
    print("========================")
    print("Files:", result["total_files"])
    print("Broken imports:", len(result["broken_imports"]))
    print("Orphan files:", len(result["orphan_files"]))
    print("Core candidates:", len(result["core_candidates"]))

    # сохраняем результат
    with open("system_map.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("\n💾 Saved: system_map.json")
