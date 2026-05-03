import os
import json
import ast
from collections import defaultdict

OUTPUT_JSON = "brain_graph_v2.json"
OUTPUT_MD = "brain_graph_v2.md"


# =========================
# 📁 SCAN FILES
# =========================
def get_py_files(root="."):
    files = []
    for path, _, fns in os.walk(root):
        for f in fns:
            if f.endswith(".py"):
                files.append(os.path.join(path, f))
    return files


# =========================
# 🧠 AST ANALYSIS (REAL CALL GRAPH)
# =========================
class CallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = []
        self.imports = []

    def visit_Call(self, node):
        try:
            if hasattr(node.func, "id"):
                self.calls.append(node.func.id)
            elif hasattr(node.func, "attr"):
                self.calls.append(node.func.attr)
        except:
            pass
        self.generic_visit(node)

    def visit_Import(self, node):
        for n in node.names:
            self.imports.append(n.name)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)


def analyze_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    except:
        return {"calls": [], "imports": []}

    try:
        tree = ast.parse(code)
    except:
        return {"calls": [], "imports": []}

    v = CallVisitor()
    v.visit(tree)

    return {
        "calls": v.calls,
        "imports": v.imports
    }


# =========================
# 🧠 DETECT CORE FLOW EDGES
# =========================
def detect_system_flow(files_data):
    flow = {
        "decision_to_execution": 0,
        "execution_to_learning": 0,
        "learning_to_decision": 0,
        "loop_create_module": 0
    }

    for f, data in files_data.items():
        text = f.lower()

        calls = data["calls"]

        # decision → execution
        if "decision" in text:
            if any("run_task" in c or "execute" in c for c in calls):
                flow["decision_to_execution"] += 1

        # execution → learning
        if "execution" in text:
            if any("learn" in c for c in calls):
                flow["execution_to_learning"] += 1

        # learning → decision
        if "learning" in text:
            if any("decide" in c for c in calls):
                flow["learning_to_decision"] += 1

        # loop detection
        if any("create_module" in c for c in calls):
            flow["loop_create_module"] += 1

    return flow


# =========================
# 🧠 MODULE DOMINANCE
# =========================
def detect_module_dominance(files_data):
    dominance = defaultdict(int)

    for _, data in files_data.items():
        for c in data["calls"]:
            if "module_auto" in c:
                dominance["module_auto"] += 1
            if "run_module" in c:
                dominance["run_module"] += 1
            if "create_module" in c:
                dominance["create_module"] += 1

    total = sum(dominance.values()) or 1

    return {
        k: round(v / total, 3)
        for k, v in dominance.items()
    }


# =========================
# 🧠 LEARNING EFFECTIVENESS
# =========================
def detect_learning_health(files_data):
    score = {
        "snapshot_usage": 0,
        "learning_hooks": 0,
        "decision_influence": 0
    }

    for _, data in files_data.items():
        imports = data["imports"]

        if any("snapshot" in i for i in imports):
            score["snapshot_usage"] += 1

        if any("learn" in i for i in imports):
            score["learning_hooks"] += 1

        if any("decision" in i for i in imports):
            score["decision_influence"] += 1

    return score


# =========================
# 🚀 BUILD BRAIN GRAPH
# =========================
def build_brain_graph():
    files = get_py_files()

    files_data = {}

    for f in files:
        files_data[f] = analyze_file(f)

    flow = detect_system_flow(files_data)
    dominance = detect_module_dominance(files_data)
    learning = detect_learning_health(files_data)

    brain = {
        "stats": {
            "files": len(files_data)
        },
        "flow": flow,
        "module_dominance": dominance,
        "learning_health": learning
    }

    return brain


# =========================
# 📦 SAVE OUTPUT
# =========================
def save_json(data):
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_md(data):
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:

        f.write("# 🧠 MEGABOT BRAIN GRAPH v2\n\n")

        f.write("## 🔁 FLOW\n")
        for k, v in data["flow"].items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## 📊 MODULE DOMINANCE\n")
        for k, v in data["module_dominance"].items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## 🧠 LEARNING HEALTH\n")
        for k, v in data["learning_health"].items():
            f.write(f"- {k}: {v}\n")


# =========================
# 🚀 MAIN
# =========================
def export_brain_graph_v2():
    print("[BRAIN GRAPH V2] scanning system...")

    brain = build_brain_graph()

    save_json(brain)
    save_md(brain)

    print("[BRAIN GRAPH V2] saved → brain_graph_v2.json / .md")

    print("FLOW:", brain["flow"])
    print("DOMINANCE:", brain["module_dominance"])

    return brain
