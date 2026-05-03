import requests
import json
import re
from collections import defaultdict

MEM_FILE = "internet_memory_v2.json"


# =========================
# 💾 MEMORY
# =========================
def load_memory():
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_memory(memory):
    try:
        with open(MEM_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except:
        pass


# =========================
# 🌐 GITHUB FETCH (STABLE)
# =========================
def fetch_repo_code(url):
    try:
        if "github.com" in url and "raw" not in url:
            url = url.replace("github.com", "raw.githubusercontent.com")
            url = url.replace("/blob/", "/")

        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
    except:
        pass

    return ""


# =========================
# 🧠 PATTERN EXTRACTION
# =========================
def extract_patterns(code):
    patterns = defaultdict(int)

    # функции
    for f in re.findall(r"def ([a-zA-Z_]+)\(", code):
        patterns[f"func:{f}"] += 1

    # классы
    for c in re.findall(r"class ([a-zA-Z_]+)", code):
        patterns[f"class:{c}"] += 2

    # сигналы архитектуры
    if "try:" in code:
        patterns["error_handling"] += 3
    if "import " in code:
        patterns["imports"] += 2
    if "for " in code:
        patterns["loop_for"] += 1
    if "while " in code:
        patterns["loop_while"] += 1

    return dict(patterns)


# =========================
# 📊 SCORING (WEIGHTED)
# =========================
def score_patterns(patterns):
    score = 0

    for p, w in patterns.items():
        if "error_handling" in p:
            score += 5 * w
        elif "class:" in p:
            score += 3 * w
        elif "func:" in p:
            score += 2 * w
        elif "loop" in p:
            score += 1 * w
        elif "imports" in p:
            score += 1

    return score


# =========================
# 🧠 MERGE MEMORY (IMPORTANT FIX)
# =========================
def merge_memory(memory, new_item):
    for item in memory:
        if item.get("url") == new_item["url"]:
            item["score"] = (item.get("score", 0) + new_item["score"]) / 2
            for k, v in new_item["patterns"].items():
                item["patterns"][k] = item["patterns"].get(k, 0) + v
            return memory

    memory.append(new_item)
    return memory


# =========================
# 🚀 MAIN LEARN FUNCTION
# =========================
def learn_from_github(repo_urls):
    memory = load_memory()

    for url in repo_urls:
        code = fetch_repo_code(url)

        if not code:
            continue

        patterns = extract_patterns(code)
        score = score_patterns(patterns)

        new_item = {
            "source": "github",
            "url": url,
            "patterns": patterns,
            "score": score
        }

        memory = merge_memory(memory, new_item)

    # ограничение памяти
    memory = memory[-2000:]

    save_memory(memory)

    return memory
