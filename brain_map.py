import os
import ast
import json
from collections import defaultdict

ROOT = "."

IGNORE_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules"
}

# =========================
# 📦 КЛАССИФИКАЦИЯ СЛОЁВ
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
# 📂 СКАН РЕПОЗИТОРИЯ (ПОЛНЫЙ + ФИЛЬТРЫ)
# =========================
def scan_files():
    files = []

    for root, dirs, fs in os.walk(ROOT):

        # 🚫 игнор системных папок
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for f in fs:
            full_path = os.path.join(root, f)
            rel = full_path.replace("\\", "/")
            files.append(rel)

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
# 🔗 IMPORTS (PY ONLY)
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
# 🧠 ПОПЫТКА ПОНИМАНИЯ ФАЙЛА
# =========================
def guess_purpose(path: str):
    name = os.path.basename(path).lower()

    if "test" in name:
        return "TEST"
    if "control" in name:
        return "CONTROL"
    if "run" in name or "main" in name:
        return "ENTRYPOINT"
    if "config" in name:
        return "CONFIG"
    if "util" in name or "helper" in name:
        return "UTILITY"
    return "UNKNOWN"


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
        "purpose": defaultdict(list),
        "imports": {},
        "file_to_file_edges": [],
        "orphans": [],
    }

    # file -> module mapping (для связей)
    file_module_map = {}

    # =========================
    # 1. базовая индексация
    # =========================
    for f in files:
        rel = f

        layer = classify(rel)
        ftype = detect_type(rel)
        purpose = guess_purpose(rel)

        brain["layers"][layer].append(rel)
        brain["file_types"][ftype].append(rel)
        brain["purpose"][purpose].append(rel)

        imports = extract_imports(f)
        brain["imports"][rel] = imports

        # module name approximation
        file_module_map[rel] = rel.replace("/", ".").replace(".py", "")

    # =========================
    # 2. file → file edges (ВАЖНО)
    # =========================
    module_to_file = {v: k for k, v in file_module_map.items()}

    for file, imports in brain["imports"].items():
        for imp in imports:
            if imp in module_to_file:
                brain["file_to_file_edges"].append({
                    "from": file,
                    "to": module_to_file[imp]
                })

    # =========================
    # 3. ORPHANS (реальная логика)
    # =========================
    used_files = set()

    for edge in brain["file_to_file_edges"]:
        used_files.add(edge["to"])

    for f in files:
        if f.endswith(".py") and f not in used_files:
            brain["orphans"].append(f)

    return brain


# =========================
# 📊 ОТЧЁТ
# =========================
def print_report(brain):
    print("\n🧠 MEGABOT BRAIN MAP v3")
    print("=" * 45)

    print("\n📦 FILES:", brain["stats"]["total_files"])

    print("\n🧩 LAYERS:")
    for k, v in brain["layers"].items():
        print(f"  {k}: {len(v)}")

    print("\n📁 FILE TYPES:")
    for k, v in brain["file_types"].items():
        print(f"  {k}: {len(v)}")

    print("\n🎯 PURPOSE:")
    for k, v in brain["purpose"].items():
        print(f"  {k}: {len(v)}")

    print("\n⚠ ORPHANS:", len(brain["orphans"]))

    print("\n🔗 FILE EDGES:", len(brain["file_to_file_edges"]))

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
