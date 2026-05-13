import os
import ast
import json
from collections import defaultdict

ROOT = "."

# =========================
# 📦 КЛАССИФИКАЦИЯ СИСТЕМЫ
# =========================
def classify(path: str):
    if "core" in path:
        return "CORE"
    if "megabot_core" in path:
        return "MEGABOT_CORE"
    if "modules" in path:
        return "MODULE"
    if ".github" in path:
        return "GITHUB"
    if "meta" in path:
        return "META"
    return "OTHER"


# =========================
# 📂 СКАН ВСЕХ ФАЙЛОВ (НЕ ТОЛЬКО .PY)
# =========================
def scan_files():
    files = []
    for root, _, fs in os.walk(ROOT):
        for f in fs:
            full_path = os.path.join(root, f)
            files.append(full_path.replace("\\", "/"))
    return files


# =========================
# 🧠 ОПРЕДЕЛЕНИЕ ТИПА ФАЙЛА
# =========================
def detect_type(path: str):
    ext = os.path.splitext(path)[1]

    mapping = {
        ".py": "python",
        ".json": "json",
        ".yml": "workflow",
        ".yaml": "workflow",
        ".md": "docs",
        ".txt": "text",
        ".sh": "script",
        ".cfg": "config",
        ".ini": "config",
        ".env": "env"
    }

    return mapping.get(ext, "other")


# =========================
# 🔗 ИМПОРТЫ (ТОЛЬКО PY)
# =========================
def extract_imports(file_path):
    if not file_path.endswith(".py"):
        return []

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
        return [f"ERROR: {e}"]


# =========================
# 🧠 ПОСТРОЕНИЕ КАРТЫ МОЗГА
# =========================
def build_brain_map():
    files = scan_files()

    brain = {
        "stats": {
            "total_files": len(files),
        },
        "layers": defaultdict(list),
        "file_types": defaultdict(list),
        "imports": {},
        "edges": [],
        "orphans": [],
        "repository": defaultdict(list)
    }

    used_modules = set()

    for f in files:
        rel = f.replace("\\", "/")

        layer = classify(rel)
        ftype = detect_type(rel)

        brain["layers"][layer].append(rel)
        brain["file_types"][ftype].append(rel)

        brain["repository"][ftype].append(rel)

        imports = extract_imports(f)
        brain["imports"][rel] = imports

        for imp in imports:
            used_modules.add(imp.split(".")[0])

    # =========================
    # 🔗 BUILD EDGES (IMPORT GRAPH)
    # =========================
    for file, imports in brain["imports"].items():
        for imp in imports:
            brain["edges"].append({
                "from": file,
                "to": imp
            })

    # =========================
    # 🧩 ORPHAN DETECTION (УМНАЯ ВЕРСИЯ)
    # =========================
    all_used = set()

    for imports in brain["imports"].values():
        for imp in imports:
            all_used.add(imp.split(".")[0])

    for f in files:
        name = os.path.basename(f).replace(".py", "")
        if name not in str(all_used):
            if f.endswith(".py"):
                brain["orphans"].append(f)

    return brain


# =========================
# 📊 ОТЧЁТ
# =========================
def print_report(brain):
    print("\n🧠 MEGABOT BRAIN MAP v2")
    print("=" * 45)

    print("\n📦 FILES:", brain["stats"]["total_files"])

    print("\n🧩 LAYERS:")
    for layer, items in brain["layers"].items():
        print(f"  {layer}: {len(items)}")

    print("\n📁 FILE TYPES:")
    for t, items in brain["file_types"].items():
        print(f"  {t}: {len(items)}")

    print("\n⚠ ORPHANS:", len(brain["orphans"]))

    print("\n🔗 EDGES:", len(brain["edges"]))

    print("\n🔍 SAMPLE IMPORTS:")
    sample = list(brain["imports"].items())[:5]
    for k, v in sample:
        print(f"  {k} → {v[:3]}")


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    brain = build_brain_map()

    print_report(brain)

    with open("brain_map.json", "w", encoding="utf-8") as f:
        json.dump(brain, f, indent=2, ensure_ascii=False)

    print("\n💾 Saved: brain_map.json")
