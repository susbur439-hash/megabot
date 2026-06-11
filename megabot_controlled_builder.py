import os
import json
import ast
import re
import time

try:
    import requests
except:
    requests = None

# =========================================================
# CONFIG
# =========================================================

GITHUB_TOKEN = os.getenv("MODELS_TOKEN")
URL = "https://models.github.ai/inference/chat/completions"

DEBUG = True

MODELS = [
    "gpt-4o-mini",
    "gpt-4o"
]


# =========================================================
# MODEL CALL (FULL DEBUG)
# =========================================================

def try_model(model, prompt):

    if not requests:
        return None, {"error": "NO_REQUESTS"}

    if not GITHUB_TOKEN:
        return None, {"error": "NO_TOKEN"}

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    try:
        print("\n" + "="*60)
        print("📤 SENDING TO MODEL:", model)
        print("="*60)
        print(prompt[:1500])
        print("="*60)

        r = requests.post(URL, json=payload, headers=headers, timeout=30)

        print("📥 STATUS:", r.status_code)

        if r.status_code != 200:
            print("❌ ERROR RESPONSE:", r.text[:500])
            return None, {"error": r.text[:300], "model": model}

        data = r.json()

        if DEBUG:
            print("\n📦 RAW AI RESPONSE:\n")
            print(json.dumps(data, indent=2)[:2000])

        text = ""

        try:
            text = data["choices"][0]["message"]["content"]
        except:
            try:
                text = data["output"][0]["content"][0]["text"]
            except:
                text = str(data)

        print("\n🧠 PARSED TEXT:\n", text[:1500])

        return {
            "text": text,
            "model": model
        }, None

    except Exception as e:
        print("🔥 EXCEPTION:", str(e))
        return None, {"error": str(e), "model": model}


def ask_model(prompt):

    if not GITHUB_TOKEN:
        return {"error": "NO_TOKEN"}

    last_error = None

    for m in MODELS:

        res, err = try_model(m, prompt)

        if res and res.get("text"):
            return res

        last_error = err
        time.sleep(0.3)

    return {
        "error": "ALL_FAILED",
        "last_error": last_error
    }


# =========================================================
# =========================================================
# TOKEN / MODEL DIAGNOSTICS
# =========================================================

def token_diagnostics():

    print("\n" + "=" * 60)
    print("🔑 TOKEN DIAGNOSTICS")
    print("=" * 60)

    if not GITHUB_TOKEN:
        print("❌ MODELS_TOKEN NOT FOUND")
        return

    print("✅ TOKEN FOUND")
    print("TOKEN LENGTH:", len(GITHUB_TOKEN))
    print("TOKEN PREFIX:", GITHUB_TOKEN[:8] + "...")

    print("\n🤖 MODELS CONFIGURED:")

    for m in MODELS:
        print(" -", m)

    if not requests:
        print("❌ requests module missing")
        return

    try:

        r = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}"
            },
            timeout=20
        )

        print("\n📡 GITHUB API CHECK")
        print("STATUS:", r.status_code)
        print("BODY:", r.text[:500])

    except Exception as e:

        print("❌ GITHUB API ERROR:", str(e))

    print("\n🧪 MODEL ACCESS TEST")

    for model in MODELS:

        try:

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": "hello"
                    }
                ]
            }

            r = requests.post(
                URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Content-Type": "application/json"
                },
                timeout=20
            )

            print("\nMODEL:", model)
            print("STATUS:", r.status_code)
            print("RESPONSE:", r.text[:500])

        except Exception as e:

            print("MODEL:", model)
            print("ERROR:", str(e))

    print("=" * 60)
# GRAPH HELPERS
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
# GRAPH BUILD (WITH DEBUG)
# =========================================================

def build_graph(files, modules):

    graph = {m: set() for m in modules}
    reverse = {m: set() for m in modules}

    module_usage = {}

    for f in files:

        name = os.path.basename(f).replace(".py", "")

        if name not in graph:
            continue

        code = read_file(f)

        refs = extract_calls(code) + extract_imports(code)

        module_usage[name] = refs

        for r in refs:
            for m in modules:
                if m in r and m != name:
                    graph[name].add(m)
                    reverse[m].add(name)

    print("\n📊 MODULE CONNECTION SAMPLE:")
    for k in list(graph.keys())[:10]:
        print(k, "->", list(graph[k]))

    return graph, reverse, module_usage


# =========================================================
# REAL SCORE
# =========================================================

def compute_real_score(graph, reverse, isolated):

    total_nodes = len(graph)

    if total_nodes == 0:
        return 0

    connectivity = sum(len(graph[n]) + len(reverse[n]) for n in graph)
    isolation_penalty = len(isolated) * 2

    score = max(0, min(100,
        int((connectivity / (total_nodes * 2)) * 100) - isolation_penalty
    ))

    return score


# =========================================================
# AI ANALYSIS
# =========================================================

def ai_analyze(graph, reverse, hubs, isolated, brain):

    real_score = compute_real_score(graph, reverse, isolated)

    prompt = f"""
You are analyzing a Python system architecture.

IMPORTANT:
- DO NOT guess score
- DO NOT output JSON
- ONLY explain problems

SYSTEM STATE:
BRAIN: {brain}
HUBS: {len(hubs)}
ISOLATED: {len(isolated)}

ISOLATED SAMPLE:
{isolated[:30]}

TASK:
Explain WHY system has so many isolated modules.
"""

    result = ask_model(prompt)

    text = result.get("text", "")

    print("\n🧠 AI FINAL ANSWER:\n")
    print(text)

    # 🔥 CRITICAL DEBUG: WHY SCORE FAILS
    score_match = re.findall(r"(\d{1,3})", text)

    print("\n🔎 NUMBERS FOUND IN AI TEXT:", score_match)

    return {
        "text": text,
        "score": real_score,
        "isolated_sample": isolated[:20],
        "hubs_sample": hubs[:20]
    }


# =========================================================
# ANALYTICS
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

    for n in isolated[:30]:
        actions.append({"type": "connect", "target": n})

    for n in hubs:
        actions.append({"type": "optimize", "target": n})

    return actions


# =========================================================
# MAIN LOOP
# =========================================================

def build_cycle():
token_diagnostics()

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

    graph, reverse, usage = build_graph(files, modules)

    brain = find_brain(graph, reverse)
    hubs = compute_hubs(graph, reverse)
    isolated = compute_isolated(graph, reverse)
    actions = decide(hubs, isolated)

    ai = ai_analyze(graph, reverse, hubs, isolated, brain)

    print("\n" + "=" * 60)
    print("MEGABOT AI DEBUG REPORT")
    print("=" * 60)
    print("BRAIN:", brain)
    print("HUBS:", len(hubs))
    print("ISOLATED:", len(isolated))
    print("ACTIONS:", len(actions))
    print("REAL_SCORE:", ai["score"])
    print("=" * 60)

    print("\n🔥 TOP PROBLEM:")
    print("ISOLATED MODULES:", len(isolated))
    print("GRAPH SIZE:", len(graph))

    return ai


if __name__ == "__main__":
    build_cycle()