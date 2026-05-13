import os
import ast
import json
from collections import defaultdict


# =========================================================
# 🧠 ROLE PATTERNS
# =========================================================

ROLE_PATTERNS = {
    "CONTROL": [
        "router",
        "control",
        "panel",
        "gateway",
        "guard"
    ],

    "DECISION": [
        "decision",
        "brain",
        "choose",
        "planner",
        "director"
    ],

    "EXECUTION": [
        "execute",
        "execution",
        "action",
        "run",
        "write",
        "create"
    ],

    "MEMORY": [
        "memory",
        "snapshot",
        "storage",
        "save",
        "load"
    ],

    "ANALYSIS": [
        "analysis",
        "analyze",
        "scan",
        "inspect",
        "detect"
    ],

    "LEARNING": [
        "learn",
        "learning",
        "adaptive",
        "reward",
        "experience"
    ]
}


# =========================================================
# 📂 FILE SCAN
# =========================================================

def scan_python_files():

    result = []

    for root, _, files in os.walk("."):

        for file in files:

            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)

            result.append(
                path.replace("\\", "/")
            )

    return result


# =========================================================
# 📦 IMPORT EXTRACTION
# =========================================================

def extract_imports(path):

    imports = []

    try:

        with open(path, "r", encoding="utf-8") as f:

            tree = ast.parse(f.read())

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for n in node.names:
                    imports.append(n.name)

            elif isinstance(node, ast.ImportFrom):

                if node.module:
                    imports.append(node.module)

    except Exception:

        pass

    return imports


# =========================================================
# 🧠 FUNCTION EXTRACTION
# =========================================================

def extract_functions(path):

    functions = []

    try:

        with open(path, "r", encoding="utf-8") as f:

            tree = ast.parse(f.read())

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

    except Exception:

        pass

    return functions


# =========================================================
# 🧠 ROLE DETECTION
# =========================================================

def detect_role(path, imports, functions):

    text = (
        path.lower()
        + " "
        + " ".join(imports).lower()
        + " "
        + " ".join(functions).lower()
    )

    scores = defaultdict(int)

    for role, patterns in ROLE_PATTERNS.items():

        for p in patterns:

            if p in text:
                scores[role] += 1

    if not scores:
        return "UNKNOWN"

    return max(scores, key=scores.get)


# =========================================================
# 🔗 BUILD EDGES
# =========================================================

def build_edges(all_data):

    edges = []

    for file, data in all_data.items():

        for imp in data["imports"]:

            edges.append({
                "from": file,
                "to": imp
            })

    return edges


# =========================================================
# 💀 DEAD MODULES
# =========================================================

def detect_dead_modules(all_data):

    used = set()

    for file, data in all_data.items():

        for imp in data["imports"]:

            used.add(
                imp.split(".")[-1]
            )

    dead = []

    for file in all_data:

        name = os.path.basename(file)

        module_name = name.replace(".py", "")

        if module_name not in used:
            dead.append(file)

    return dead


# =========================================================
# 🧠 ANALYZE SYSTEM
# =========================================================

def analyze():

    files = scan_python_files()

    result = {
        "stats": {},
        "roles": defaultdict(list),
        "imports": {},
        "functions": {},
        "edges": [],
        "dead_modules": [],
        "broken_imports": [],
        "duplicates": []
    }

    all_data = {}

    for file in files:

        imports = extract_imports(file)

        functions = extract_functions(file)

        role = detect_role(
            file,
            imports,
            functions
        )

        result["roles"][role].append(file)

        result["imports"][file] = imports

        result["functions"][file] = functions

        all_data[file] = {
            "imports": imports,
            "functions": functions,
            "role": role
        }

    # =========================
    # 🔗 EDGES
    # =========================

    result["edges"] = build_edges(all_data)

    # =========================
    # 💀 DEAD MODULES
    # =========================

    result["dead_modules"] = detect_dead_modules(all_data)

    # =========================
    # 📊 STATS
    # =========================

    result["stats"] = {
        "files": len(files),
        "edges": len(result["edges"]),
        "dead_modules": len(result["dead_modules"])
    }

    return result


# =========================================================
# 🚀 RUN
# =========================================================

def run(data=None):

    print("\n🧠 ARCHITECTURE ANALYZER START\n")

    result = analyze()

    print("📦 FILES:", result["stats"]["files"])
    print("🔗 EDGES:", result["stats"]["edges"])
    print("💀 DEAD:", result["stats"]["dead_modules"])

    print("\n🧠 ROLES:")

    for role, items in result["roles"].items():

        print(f"  {role}: {len(items)}")

    with open(
        "architecture_analysis.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n💾 Saved: architecture_analysis.json")

    return result
