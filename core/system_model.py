import os
import ast
from collections import defaultdict

ROOT = "."

# =========================================================
# 🧠 SYSTEM MODEL v1 (SEMANTIC LAYER)
# =========================================================

ROLE_MAP = {
    "CONTROL": ["control", "router", "bus", "gateway", "panel"],
    "DECISION": ["brain", "decision", "director", "controller"],
    "EXECUTION": ["execution", "executor", "run", "action"],
    "ANALYSIS": ["analysis", "analyzer", "scan", "observer"],
    "MEMORY": ["memory", "snapshot", "storage"],
    "LEARNING": ["learn", "adaptive", "learning"]
}


# =========================================================
# 📂 SCAN ALL FILES
# =========================================================

def scan_files():
    files = []
    for root, _, fs in os.walk(ROOT):
        for f in fs:
            files.append(os.path.join(root, f).replace("\\", "/"))
    return files


# =========================================================
# 🧠 ROLE DETECTION
# =========================================================

def detect_role(path: str):
    p = path.lower()

    for role, keys in ROLE_MAP.items():
        for k in keys:
            if k in p:
                return role

    return "UNKNOWN"


# =========================================================
# 🔗 IMPORT GRAPH
# =========================================================

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


# =========================================================
# 🧠 BUILD SYSTEM GRAPH
# =========================================================

def build_system_model():

    files = scan_files()

    model = {
        "stats": {
            "total_files": len(files)
        },

        "roles": defaultdict(list),
        "role_graph": defaultdict(set),

        "file_roles": {},
        "imports": {},

        "flow": [
            "CONTROL",
            "DECISION",
            "ANALYSIS",
            "EXECUTION",
            "MEMORY"
        ],

        "unknown": []
    }

    # =========================
    # STEP 1: classify files
    # =========================
    for f in files:

        role = detect_role(f)
        imports = extract_imports(f)

        model["file_roles"][f] = role
        model["roles"][role].append(f)
        model["imports"][f] = imports

        if role == "UNKNOWN" and f.endswith(".py"):
            model["unknown"].append(f)

    # =========================
    # STEP 2: build semantic links
    # =========================
    for file, imports in model["imports"].items():

        file_role = model["file_roles"].get(file, "UNKNOWN")

        for imp in imports:
            imp_name = imp.split(".")[0]

            for f, r in model["file_roles"].items():
                if imp_name in f:
                    model["role_graph"][file_role].add(r)

    # convert sets → lists for json
    model["role_graph"] = {
        k: list(v) for k, v in model["role_graph"].items()
    }

    return model


# =========================================================
# 📊 REPORT
# =========================================================

def print_report(model):

    print("\n🧠 SYSTEM MODEL v1")
    print("=" * 50)

    print("\n📦 FILES:", model["stats"]["total_files"])

    print("\n🧩 ROLES:")
    for r, items in model["roles"].items():
        print(f"  {r}: {len(items)}")

    print("\n🔗 ROLE GRAPH:")
    for k, v in model["role_graph"].items():
        print(f"  {k} → {v}")

    print("\n⚠ UNKNOWN:", len(model["unknown"]))

    print("\n🔁 FLOW:")
    print(" → ".join(model["flow"]))


# =========================================================
# 🚀 RUN
# =========================================================

if __name__ == "__main__":
    model = build_system_model()
    print_report(model)
