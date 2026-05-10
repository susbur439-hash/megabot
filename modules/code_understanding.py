# =========================================================
# 🧠 MEGABOT CODE UNDERSTANDING LAYER v2
# 🧠 STRUCTURE + AST + ROLES + GRAPH + SUMMARY
# =========================================================

import os
import ast
import json
from collections import defaultdict

# =========================================================
# ⚙ CONFIG
# =========================================================

ROOT_DIR = "."
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".venv"
}

MEMORY_FILE = "code_understanding.json"

# =========================================================
# 📋 LOG
# =========================================================

def log(msg):
    print(msg)

# =========================================================
# 📖 FILE READER
# =========================================================

def read_file(path):

    try:

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    except:
        return ""

# =========================================================
# 🔍 SCAN REPO
# =========================================================

def scan_repo():

    files = []

    for root, dirs, filenames in os.walk(ROOT_DIR):

        # ignore dirs
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
        ]

        for f in filenames:

            if f.endswith(".py"):

                files.append(
                    os.path.join(root, f)
                )

    return files

# =========================================================
# 🧠 AST ANALYZER
# =========================================================

def analyze_ast(code):

    result = {
        "imports": set(),
        "functions": [],
        "classes": [],
        "has_run": False,
        "has_decide": False,
        "has_execute": False,
        "has_main": False,
        "parse_error": None
    }

    try:

        tree = ast.parse(code)

        for node in ast.walk(tree):

            # =========================
            # imports
            # =========================

            if isinstance(node, ast.Import):

                for n in node.names:

                    result["imports"].add(
                        n.name.split(".")[0]
                    )

            elif isinstance(node, ast.ImportFrom):

                if node.module:

                    result["imports"].add(
                        node.module.split(".")[0]
                    )

            # =========================
            # functions
            # =========================

            elif isinstance(node, ast.FunctionDef):

                result["functions"].append(
                    node.name
                )

                if node.name == "run":
                    result["has_run"] = True

                if "decide" in node.name:
                    result["has_decide"] = True

                if "execute" in node.name:
                    result["has_execute"] = True

                if node.name == "main":
                    result["has_main"] = True

            # =========================
            # classes
            # =========================

            elif isinstance(node, ast.ClassDef):

                result["classes"].append(
                    node.name
                )

    except Exception as e:

        result["parse_error"] = str(e)

    result["imports"] = list(
        result["imports"]
    )

    return result

# =========================================================
# 🧠 ROLE CLASSIFIER
# =========================================================

def classify_role(ast_data, filename):

    name = filename.lower()

    if "director" in name:
        return "decision_orchestrator"

    if "engine" in name:
        return "execution_core"

    if "router" in name:
        return "routing_layer"

    if "control" in name:
        return "control_layer"

    if "analysis" in name:
        return "analysis_layer"

    if "decision" in name:
        return "decision_layer"

    if "learning" in name:
        return "learning_layer"

    if "memory" in name:
        return "memory_layer"

    if "module_" in name:
        return "generated_module"

    # =========================
    # AST fallback
    # =========================

    if ast_data["has_execute"]:
        return "execution_module"

    if ast_data["has_decide"]:
        return "decision_module"

    if ast_data["has_run"]:
        return "entry_module"

    return "utility"

# =========================================================
# 🔗 BUILD GRAPH
# =========================================================

def build_graph(files_data):

    graph = defaultdict(set)

    for file, data in files_data.items():

        for imp in data["ast"]["imports"]:

            graph[file].add(imp)

    return graph

# =========================================================
# 🧠 ANALYZE REPO
# =========================================================

def analyze_repo():

    files = scan_repo()

    files_data = {}

    log("🧠 Scanning repository...")

    for f in files:

        code = read_file(f)

        ast_data = analyze_ast(code)

        role = classify_role(
            ast_data,
            os.path.basename(f)
        )

        files_data[f] = {
            "role": role,
            "ast": ast_data
        }

    graph = build_graph(files_data)

    return files_data, graph

# =========================================================
# 🧠 SUMMARY
# =========================================================

def build_summary(files_data, graph):

    roles = defaultdict(list)

    for f, data in files_data.items():

        roles[data["role"]].append(f)

    return {

        "total_files": len(files_data),

        "roles": dict(roles),

        "graph_size": len(graph),

        "brain_candidates":
            roles.get(
                "decision_orchestrator",
                []
            ),

        "execution_candidates":
            roles.get(
                "execution_core",
                []
            )
    }

# =========================================================
# 💾 SAVE
# =========================================================

def save(result):

    # =========================
    # save json
    # =========================

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )

    log(f"💾 SAVED -> {MEMORY_FILE}")

    # =========================
    # auto github save
    # =========================

    try:

        os.system(
            "git add code_understanding.json"
        )

        os.system(
            'git commit -m "update code understanding"'
        )

        os.system("git push")

        log("🚀 GITHUB MEMORY UPDATED")

    except Exception as e:

        log(f"⚠️ Git save failed: {e}")

# =========================================================
# 🚀 RUN
# =========================================================

def run():

    files_data, graph = analyze_repo()

    summary = build_summary(
        files_data,
        graph
    )

    result = {

        "files": files_data,

        "graph": {
            k: list(v)
            for k, v in graph.items()
        },

        "summary": summary
    }

    log("\n==============================")
    log("🧠 CODE UNDERSTANDING COMPLETE")
    log("==============================")

    log(
        f"FILES: "
        f"{summary['total_files']}"
    )

    log(
        f"GRAPH SIZE: "
        f"{summary['graph_size']}"
    )

    log(
        f"ROLES: "
        f"{list(summary['roles'].keys())}"
    )

    log(
        f"BRAIN CANDIDATES: "
        f"{summary['brain_candidates']}"
    )

    log(
        f"EXECUTION CANDIDATES: "
        f"{summary['execution_candidates']}"
    )

    save(result)

    return result

# =========================================================
# ▶ ENTRY
# =========================================================

if __name__ == "__main__":
    run()
