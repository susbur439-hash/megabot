import requests
import json
import re

MEM_FILE = "internet_memory_v2.json"


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
# 🌐 GITHUB FETCH
# =========================
def fetch_repo_code(url):
    """
    Очень упрощённый fetch (public raw files only)
    """
    try:
        if "github.com" in url:
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
    patterns = []

    # функции
    functions = re.findall(r"def ([a-zA-Z_]+)\(", code)
    for f in functions:
        patterns.append(f"func:{f}")

    # классы
    classes = re.findall(r"class ([a-zA-Z_]+)", code)
    for c in classes:
        patterns.append(f"class:{c}")

    # важные конструкции
    if "for " in code:
        patterns.append("loop_for")
    if "while " in code:
        patterns.append("loop_while")
    if "import " in code:
        patterns.append("imports")
    if "try:" in code:
        patterns.append("error_handling")

    return patterns


# =========================
# 📊 SCORING
# =========================
def score_patterns(patterns):
    score = 0

    for p in patterns:
        if "error_handling" in p:
            score += 5
        if "class:" in p:
            score += 3
        if "func:" in p:
            score += 2
        if "loop" in p:
            score += 1

    return score


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

        memory.append({
            "source": "github",
            "url": url,
            "patterns": patterns,
            "score": score
        })

    # ограничение памяти
    memory = memory[-2000:]

    save_memory(memory)

    return memory
