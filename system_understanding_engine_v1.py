import os
import ast
from collections import defaultdict

ROOT = "."

# =========================
# 🧠 РОЛИ СИСТЕМЫ
# =========================
ROLE_KEYWORDS = {
    "ENTRYPOINT": ["main", "run", "start", "app", "bot_start"],
    "CONTROL": ["control", "panel", "gateway", "router", "bus"],
    "DECISION_ENGINE": ["decision", "brain", "controller"],
    "EXECUTOR": ["execution", "executor", "run", "action"],
    "ANALYZER": ["analysis", "analyzer", "inspect", "scan"],
    "MEMORY": ["memory", "storage", "snapshot"],
    "LEARNING": ["learn", "learning", "adaptive"]
}


# =========================
# 📂 СКАН ВСЕХ ФАЙЛОВ
# =========================
def scan_files():
    all_files = []
    for root, _, files in os.walk(ROOT):
        for f in files:
            all_files.append(os.path.join(root, f).replace("\\", "/"))
    return all_files


# =========================
# 🧩 ОПРЕДЕЛЕНИЕ РОЛИ
# =========================
def detect_role(path: str):
    lower = path.lower()

    for role, keywords in ROLE_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return role

    return "UNKNOWN"


# =========================
# 📁 ТИП ФАЙЛА
# =========================
def detect_type(path: str):
    ext = os.path.splitext(path)[1]

    mapping = {
        ".py": "python",
        ".json": "json",
        ".md": "docs",
        ".txt": "text",
        ".yml": "workflow",
        ".yaml": "workflow",
        ".sh": "script",
        ".cfg": "config",
        ".ini": "config"
    }

    return mapping.get(ext, "other")


# =========================
# 🔗 ИМПОРТЫ
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

    except:
        return []


# =========================
# 🧠 FLOW ВЫПОЛНЕНИЯ (ПРОСТАЯ МОДЕЛЬ)
# =========================
def build_flow_map():
    return [
        "CONTROL",
        "ENTRYPOINT",
        "ANALYZER",
        "DECISION_ENGINE",
        "EXECUTOR",
        "MEMORY"
    ]


# =========================
# 🧠 ENGINE
# =========================
def build_system_model():
    files = scan_files()

    model = {
        "stats": {
            "total_files": len(files)
        },
        "roles": defaultdict(list),
        "types": defaultdict(list),
        "imports": {},
        "flow": build_flow_map(),
        "unknown_files": []
    }

    for f in files:
        role = detect_role(f)
        ftype = detect_type(f)
        imports = extract_imports(f)

        model["roles"][role].append(f)
        model["types"][ftype].append(f)
        model["imports"][f] = imports

        if role == "UNKNOWN" and f.endswith(".py"):
            model["unknown_files"].append(f)

    return model


# =========================
# 📊 ОТЧЁТ
# =========================
def print_report(model):
    print("\n🧠 MEGABOT SYSTEM UNDERSTANDING ENGINE v1")
    print("=" * 55)

    print("\n📦 TOTAL FILES:", model["stats"]["total_files"])

    print("\n🧩 ROLES:")
    for role, items in model["roles"].items():
        print(f"  {role}: {len(items)}")

    print("\n📁 TYPES:")
    for t, items in model["types"].items():
        print(f"  {t}: {len(items)}")

    print("\n🔁 FLOW:")
    print("  → ".join(model["flow"]))

    print("\n⚠ UNKNOWN FILES:", len(model["unknown_files"]))

    print("\n🔍 SAMPLE IMPORTS:")
    sample = list(model["imports"].items())[:5]
    for k, v in sample:
        print(f"  {k} → {v[:3]}")


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    model = build_system_model()
    print_report(model)
