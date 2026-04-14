import os
import json

BASE_DIR = "megabot_core"

STRUCTURE = {
    "run.py": '''
from control_panel import run

if __name__ == "__main__":
    run()
''',

    "observer.py": '''
import os

def scan_project(root):
    report = {
        "files": [],
        "empty_files": [],
        "dirs": []
    }

    for path, dirs, files in os.walk(root):
        for d in dirs:
            report["dirs"].append(os.path.join(path, d))

        for f in files:
            full = os.path.join(path, f)
            report["files"].append(full)

            try:
                if os.path.getsize(full) == 0:
                    report["empty_files"].append(full)
            except:
                pass

    return report
''',

    "analyzer.py": '''
import os

def analyze(report):
    result = {
        "problems": [],
        "actions": []
    }

    files = report.get("files", [])
    empty = report.get("empty_files", [])

    # пустые файлы
    for f in empty:
        result["problems"].append(f"empty_file: {f}")
        result["actions"].append({
            "type": "delete_file",
            "path": f
        })

    # подозрительные setup
    for f in files:
        name = os.path.basename(f)
        if name.startswith("setup"):
            result["problems"].append(f"suspicious: {f}")
            result["actions"].append({
                "type": "delete_file",
                "path": f
            })

    # большие файлы
    for f in files:
        try:
            if os.path.getsize(f) > 5000:
                result["problems"].append(f"large_file: {f}")
        except:
            pass

    return result
''',

    "execution.py": '''
import os

def execute(actions):
    result = []

    for act in actions:
        t = act.get("type")
        path = act.get("path")

        try:
            if t == "delete_file":
                if os.path.exists(path):
                    os.remove(path)
                    result.append(f"deleted: {path}")

            elif t == "read_file":
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    result.append({path: content[:200]})

        except Exception as e:
            result.append(f"error: {path} -> {e}")

    return result
''',

    "control_panel.py": '''
import json
from observer import scan_project
from analyzer import analyze
from execution import execute

def run():
    print("=== MEGABOT CORE (СРЕДНИЙ УРОВЕНЬ) ===")

    while True:
        cmd = input("\\nscan / fix / exit:\\n")

        if cmd == "exit":
            break

        elif cmd == "scan":
            report = scan_project(".")
            analysis = analyze(report)

            print("\\n=== ANALYSIS ===")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))

        elif cmd == "fix":
            report = scan_project(".")
            analysis = analyze(report)

            actions = analysis.get("actions", [])
            result = execute(actions)

            print("\\n=== FIX RESULT ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        else:
            print("unknown command")
'''
}

def create():
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)

    for filename, content in STRUCTURE.items():
        path = os.path.join(BASE_DIR, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())

    print("✅ Megabot Core создан!")

if __name__ == "__main__":
    create()
