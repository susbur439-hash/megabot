import os
import json
import ast
import hashlib
import re
import time

# =========================================================
# 📦 SAFE IMPORT
# =========================================================

try:
    import requests
except:
    requests = None

from modules.control_bus import emit


# =========================================================
# 🧠 CONFIG
# =========================================================

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")

MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "Meta-Llama-3.1-8B-Instruct",
    "Meta-Llama-3.1-405B-Instruct"
]

URL = "https://models.github.ai/inference/chat/completions"


# =========================================================
# 🤖 MODEL CALL
# =========================================================

def try_model(model, prompt):
    if not requests:
        return None, {"error": "requests missing"}

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

        # 🚨 RATE LIMIT FIX
        if r.status_code == 429:
            return None, {"error": "RATE_LIMIT", "model": model}

        if r.status_code != 200:
            return None, {"error": r.text, "status": r.status_code, "model": model}

        data = r.json()

        text = ""
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


def ask_model(prompt):
    if not GITHUB_TOKEN:
        return {"error": "NO_TOKEN"}

    if not requests:
        return {"error": "NO_REQUESTS"}

    last_error = None

    for model in MODELS:

        result, error = try_model(model, prompt)

        if result:
            return result

        last_error = error

        # ⛔ защита от спама GitHub
        time.sleep(1)

    return {
        "error": "ALL_MODELS_FAILED",
        "last_error": last_error
    }


# =========================================================
# 📊 LOG
# =========================================================

def log(x):
    print(x)


# =========================================================
# 🧠 GRAPH ANALYSIS
# =========================================================

def extract_imports(code):
    out = []
    try:
        tree = ast.parse(code)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for i in n.names:
                    out.append(i.name)
            elif isinstance(n, ast.ImportFrom):
                if n.module:
                    out.append(n.module)
    except:
        pass
    return out


def extract_calls(code):
    out = []
    try:
        tree = ast.parse(code)
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    out.append(n.func.id)
                elif isinstance(n.func, ast.Attribute):
                    out.append(n.func.attr)
    except:
        pass
    return out


def read_file(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


# =========================================================
# 🤖 AI ANALYSIS
# =========================================================

def ai_analyze(graph, reverse, hubs, isolated, brain):

    prompt = f"""
Analyze Megabot architecture.

Give:
- problems
- weak points
- improvements
- score: N (0-100)

BRAIN: {brain}
HUBS: {hubs}
ISOLATED: {isolated}

GRAPH:
{json.dumps({k: list(v) for k, v in graph.items()}, indent=2)}
"""

    result = ask_model(prompt)

    log("AI_RAW:")
    log(json.dumps(result, indent=2))

    if "error" in result:
        return {"text": "", "score": 0, "error": result}

    text = result.get("text", "")

    # SCORE
    m = re.search(r"score\s*:\s*(\d+)", text.lower())
    score = int(m.group(1)) if m else 0

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

    for f in files:
        name = os.path.basename(f).replace(".py", "")

        if name not in graph:
            continue

        code = read_file(f)

        refs = extract_calls(code) + extract_imports(code)

        for r in refs:
            for m in modules:
                if m in r and m != name:
                    graph[name].add(m)
                    reverse[m].add(name)

    return graph, reverse


# =========================================================
# 🧠 DECISION ENGINE
# =========================================================

def find_brain(graph, reverse):

    best = None
    best_score = -1

    for n in graph:
        score = len(graph[n]) + len(reverse[n])

        if n == "director":
            score += 20

        if score > best_score:
            best = n
            best_score = score

    return best


def compute_hubs(graph, reverse):
    return [n for n in graph if len(graph[n]) + len(reverse[n]) >= 3]


def compute_isolated(graph, reverse):
    return [n for n in graph if not graph[n] and not reverse[n]]


def decide(hubs, isolated):

    actions = []

    for n in isolated:
        actions.append({"type": "connect", "target": n})

    for n in hubs:
        actions.append({"type": "optimize", "target": n})

    return actions


# =========================================================
# 🧠 MAIN
# =========================================================

def build_cycle():

    files = []
    modules = []

    for root, _, fs in os.walk("."):

        if ".git" in root or "__pycache__" in root:
            continue

        for f in fs:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                files.append(path)

                if "modules" in root:
                    modules.append(f.replace(".py", ""))

    graph, reverse = build_graph(files, modules)

    brain = find_brain(graph, reverse)
    hubs = compute_hubs(graph, reverse)
    isolated = compute_isolated(graph, reverse)
    actions = decide(hubs, isolated)

    ai = ai_analyze(graph, reverse, hubs, isolated, brain)

    log("==============================")
    log("MEGABOT AI LOOP")
    log("==============================")
    log(f"BRAIN: {brain}")
    log(f"HUBS: {len(hubs)}")
    log(f"ISOLATED: {len(isolated)}")
    log(f"AI_SCORE: {ai.get('score', 0)}")
    log("==============================")

    return ai


if __name__ == "__main__":
    build_cycle()