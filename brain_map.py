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
# 📂 СБОР PY ФАЙЛОВ
# =========================
def scan_files():
    files = []
    for root, _, fs in os.walk(ROOT):
        for f in fs:
            if f.endswith(".py"):
                files.append(os.path.join(root, f))
    return files


# =========================
# 🔗 ИМПОРТЫ
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
        "imports": {},
        "edges": [],
        "orphans": []
    }

    used_modules = set()

    for f in files:
        rel = f.replace("\\", "/")
        layer = classify(rel)

        imports = extract_imports(f)

        brain["layers"][layer].append(rel)
        brain["imports"][rel] = imports

        for imp in imports:
            used_modules.add(imp.split(".")[0])

    # =========================
    # 🧩 ORPHAN DETECTION
    # =========================
    for f in files:
        name = os.path.basename(f).replace(".py", "")
        if name not in str(brain["imports"]):
            brain["orphans"].append(f)

    return brain


# =========================
# 📊 ВЫВОД ОТЧЁТА
# =========================
def print_report(brain):
    print("\n🧠 MEGABOT BRAIN MAP v1")
    print("=" * 40)

    print("\n📦 FILES:", brain["stats"]["total_files"])

    print("\n🧩 LAYERS:")
    for layer, items in brain["layers"].items():
        print(f"  {layer}: {len(items)}")

    print("\n⚠ ORPHANS:", len(brain["orphans"]))

    print("\n🔗 SAMPLE IMPORTS:")
    sample = list(brain["imports"].items())[:5]
    for k, v in sample:
        print(f"  {k} → {v[:3]}")


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    brain = build_brain_map()

    print_report(brain)

    # сохраняем карту
    with open("brain_map.json", "w", encoding="utf-8") as f:
        json.dump(brain, f, indent=2, ensure_ascii=False)

    print("\n💾 Saved: brain_map.json")
