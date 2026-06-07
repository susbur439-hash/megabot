import os
import json
import traceback
import ast
import hashlib
import re

# =========================================================
# 📦 SAFE IMPORT (requests)
# =========================================================

try:
    import requests
except Exception as e:
    requests = None


from modules.control_bus import emit


# =========================================================
# 🧠 AI CONFIG
# =========================================================

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")

MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini",
    "gpt-3.5-turbo"
]

URL = "https://models.github.ai/inference/chat/completions"


# =========================================================
# 🤖 AI CALL (AUTO FALLBACK + DEBUG)
# =========================================================

def try_model(model, prompt):
    if not requests:
        return None, {"error": "requests not installed"}

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        r = requests.post(URL, json=payload, headers=headers, timeout=30)

        if r.status_code != 200:
            return None, {
                "error": r.text,
                "status": r.status_code,
                "model": model
            }

        data = r.json()

        try:
            text = data["choices"][0]["message"]["content"]
        except:
            text = str(data)

        return {
            "text": text,
            "raw": data,
            "model": model
        }, None

    except Exception as e:
        return None, {"error": str(e), "model": model}


def ask_model(prompt: str):

    if not GITHUB_TOKEN:
        return {"error": "MODELS_TOKEN missing"}

    if not requests:
        return {"error": "requests module missing"}

    last_error = None

    for model in MODELS:
        result, error = try_model(model, prompt)

        if result:
            return result

        last_error = error

    return {
        "error": "ALL_MODELS_FAILED",
        "last_error": last_error
    }


# =========================================================
# 🧠 CORE CONFIG
# =========================================================

ROOT_DIR = "."
MODULES_DIR = "modules"
MEMORY_FILE = "builder_memory.json"
MAX_CYCLES = 1


CORE_MODULES = {
    "director", "central_decision", "execution", "engine",
    "observer", "control_panel", "learning", "evaluation",
    "planner", "memory", "decision", "task_interpreter",
    "analysis", "router", "module_router", "control_bus"
}


# =========================================================
# 📋 LOG (DEBUG POWERED)
# =========================================================

def log(msg):
    print(msg)


# =========================================================
# 🔐 GRAPH HASH
# =========================================================

def hash_graph(graph):
    try:
        flat = {k: sorted(list(v)) for k, v in graph.items()}
        raw = json.dumps(flat, sort_keys=True).encode()
        return hashlib.md5(raw).hexdigest()
    except:
        return None


# =========================================================
# 💾 MEMORY
# =========================================================

def load_memory():
    default = {
        "cycles": 0,
        "brain_node": None,
        "hubs": [],
        "isolated": [],
        "actions": [],
        "ai_report": {},
        "ai_score": 0,
        "graph_hash": None
    }

    if not os.path.exists(MEMORY_FILE):
        return default

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for k, v in default.items():
            data.setdefault(k, v)

        return data
    except:
        return default


def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except:
        pass


# =========================================================
# 📖 FILE
# =========================================================

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


# =========================================================
# 🔍 ANALYSIS
# =========================================================

def extract_imports(code):
    imports = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except:
        pass
    return imports


def extract_calls(code):
    calls = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
    except:
        pass
    return calls


# =========================================================
# 🤖 AI ANALYSIS (ROBUST)
# =========================================================

def ai_analyze(graph, reverse, hubs, isolated, brain):

    if not GITHUB_TOKEN:
        return {"text": "", "score": 0, "status": "no_token"}

    prompt = f"""
Ты анализируешь архитектуру Megabot.

Дай:
- проблемы
- слабые места
- улучшения
- обязательно score: N (0-100)

BRAIN: {brain}
HUBS: {hubs}
ISOLATED: {isolated}

GRAPH:
{json.dumps({k: list(v) for k, v in graph.items()}, indent=2)}
"""

    result = ask_model(prompt)

    log("AI_RAW_RESPONSE:")
    log(json.dumps(result, indent=2, ensure_ascii=False))

    if isinstance(result, dict) and "error" in result:
        return {"text": "", "score": 0, "error": result["error"]}

    text = ""
    try:
        text = result["text"]
    except:
        text = str(result)

    # 🔍 SCORE EXTRACTION (2 METHODS)
    score = 0

    m = re.search(r"score\s*:\s*(\d+)", text.lower())
    if m:
        score = int(m.group(1))
    else:
        m = re.search(r"\b(\d{1,3})\b", text)
        if m:
            score = int(m.group(1))

    return {
        "text": text,
        "score": score,
        "raw": result
    }


# =========================================================
# 🔗 GRAPH BUILD
# =========================================================

def build_graph(files, modules):

    graph = {m: set() for m in modules}
    reverse = {m: set() for m in modules}

    for file in files:
        current = os.path.basename(file).replace(".py", "")

        if current not in graph:
            continue

        code = read_file(file)
        refs = extract_calls(code) + extract_imports(code)

        for ref in refs:
            for target in modules:
                if target == current:
                    continue

                if target in ref:
                    graph[current].add(target)
                    reverse[target].add(current)

    return graph, reverse


# =========================================================
# 🧠 BRAIN
# =========================================================

def find_brain(graph, reverse):
    best, best_score = None, -1

    for n in graph:
        score = len(graph[n]) + len(reverse[n])

        if n == "director":
            score += 20

        if score > best_score:
            best = n
            best_score = score

    return best


# =========================================================
# 🧠 HUBS
# =========================================================

def compute_hubs(graph, reverse):
    hubs = []

    for n in graph:
        score = len(graph[n]) + len(reverse[n])
        if score >= 3:
            hubs.append(n)

    return hubs


# =========================================================
# 🧠 ISOLATED
# =========================================================

def compute_isolated(graph, reverse):
    return [n for n in graph if not graph[n] and not reverse[n]]


# =========================================================
# 🧠 DECISION
# =========================================================

def decide(hubs, isolated):
    actions = []

    for n in isolated:
        actions.append({"type": "connect", "target": n})

    for n in hubs:
        actions.append({"type": "optimize", "target": n})

    return actions


# =========================================================
# 🧠 MAIN LOOP
# =========================================================

def build_cycle():

    memory = load_memory()

    files = []
    modules = []

    for root, _, file_list in os.walk(ROOT_DIR):
        if ".git" in root or "__pycache__" in root:
            continue

        for f in file_list:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                files.append(path)

                if os.path.basename(root) == MODULES_DIR:
                    name = f.replace(".py", "")
                    if name in CORE_MODULES:
                        modules.append(name)

    graph, reverse = build_graph(files, modules)

    brain = find_brain(graph, reverse)
    hubs = compute_hubs(graph, reverse)
    isolated = compute_isolated(graph, reverse)
    actions = decide(hubs, isolated)

    ai_report = ai_analyze(graph, reverse, hubs, isolated, brain)

    memory.update({
        "brain_node": brain,
        "hubs": hubs,
        "isolated": isolated,
        "actions": actions,
        "ai_report": ai_report,
        "ai_score": ai_report.get("score", 0),
        "graph_hash": hash_graph(graph)
    })

    memory["cycles"] += 1

    log("==============================")
    log("MEGABOT AI LOOP")
    log("==============================")
    log(f"BRAIN: {brain}")
    log(f"HUBS: {len(hubs)}")
    log(f"ISOLATED: {len(isolated)}")
    log(f"AI_SCORE: {memory['ai_score']}")
    log("==============================")

    save_memory(memory)


# =========================================================
# ▶ RUN
# =========================================================

if __name__ == "__main__":
    for _ in range(MAX_CYCLES):
        build_cycle() 