import os
import ast
from collections import defaultdict

ROOT = "."

# =========================
# 🧠 РОЛИ
# =========================
ROLE_KEYWORDS = {
    "ENTRYPOINT": ["main", "run", "start", "app", "bot_start"],
    "CONTROL": ["control", "panel", "gateway", "router", "bus"],
    "DECISION": ["decision", "brain", "controller"],
    "EXECUTION": ["execution", "executor", "action"],
    "ANALYSIS": ["analysis", "analyzer", "scan", "inspect"],
    "MEMORY": ["memory", "snapshot", "storage"],
    "LEARNING": ["learn", "learning", "adaptive"],
    "CORE": ["core", "engine"]
}

# =========================
# 📂 SCAN FILES
# =========================
def scan_files():
    files = []
    for root, _, fs in os.walk(ROOT):
        for f in fs:
            files.append(os.path.join(root, f).replace("\\", "/"))
    return files

# =========================
# 🧩 ROLE DETECTION
# =========================
def detect_role(path: str):
    lower = path.lower()

    for role, kws in ROLE_KEYWORDS.items():
        for kw in kws:
            if kw in lower:
                return role

    return "UNKNOWN"

# =========================
# 📁 FILE TYPE
# =========================
def detect_type(path: str):
    ext = os.path.splitext(path)[1]
    return {
        ".py": "python",
        ".json": "json",
        ".md": "docs",
        ".txt": "text",
        ".yml": "workflow",
        ".yaml": "workflow",
        ".sh": "script"
    }.get(ext, "other")

# =========================
# 🔗 IMPORTS
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
                imports.extend([n.name for n in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports
    except:
        return []

# =========================
# 🎯 PURPOSE DETECTION
# =========================
def detect_purpose(path: str):
    name = os.path.basename(path).lower()

    if "main" in name or "run" in name:
        return "ENTRYPOINT"
    if "control" in name or "panel" in name:
        return "CONTROL"
    if "engine" in name:
        return "ENGINE"
    if "test" in name:
        return "TEST"
    return "UTIL"

# =========================
# 🧠 BUILD MODEL
# =========================
def build_model():
    files = scan_files()

    model = {
        "stats": {"total_files": len(files)},
        "roles": defaultdict(list),
        "types": defaultdict(list),
        "purposes": defaultdict(list),
        "imports": {},
        "edges": [],
        "unknown": []
    }

    for f in files:
        role = detect_role(f)
        ftype = detect_type(f)
        purpose = detect_purpose(f)
        imports = extract_imports(f)

        model["roles"][role].append(f)
        model["types"][ftype].append(f)
        model["purposes"][purpose].append(f)
        model["imports"][f] = imports

        if role == "UNKNOWN" and f.endswith(".py"):
            model["unknown"].append(f)

    # =========================
    # 🔗 BUILD EDGES
    # =========================
    for file, imports in model["imports"].items():
        for imp in imports:
            model["edges"].append({"from": file, "to": imp})

    return model

# =========================
# 📊 SCORE ENGINE
# =========================
def architecture_score(model):
    total = model["stats"]["total_files"]
    unknown = len(model["unknown"])

    if total == 0:
        return 0

    known_ratio = (total - unknown) / total
    return round(known_ratio * 100, 2)

# =========================
# 📊 REPORT
# =========================
def print_report(model):
    print("\n🧠 MEGABOT SYSTEM UNDERSTANDING ENGINE v2 (MAX)")
    print("=" * 60)

    print("\n📦 FILES:", model["stats"]["total_files"])

    print("\n🧩 ROLES:")
    for k, v in model["roles"].items():
        print(f"  {k}: {len(v)}")

    print("\n📁 TYPES:")
    for k, v in model["types"].items():
        print(f"  {k}: {len(v)}")

    print("\n🎯 PURPOSES:")
    for k, v in model["purposes"].items():
        print(f"  {k}: {len(v)}")

    print("\n🔗 EDGES:", len(model["edges"]))
    print("⚠ UNKNOWN:", len(model["unknown"]))
    print("📊 ARCH SCORE:", architecture_score(model), "%")

# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    model = build_model()
    print_report(model)

    with open("system_model_v2.json", "w", encoding="utf-8") as f:
        import json
        json.dump(model, f, indent=2, ensure_ascii=False)

    print("\n💾 Saved: system_model_v2.json")
