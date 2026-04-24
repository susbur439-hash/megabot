import os


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def setup_meta_observer():
    print("🧠 Установка Meta-Observer...\n")

    # =========================
    # scanner.py (FIXED)
    # =========================
    scanner = '''import os

def scan_repository(root="."):
    files = []

    ignore_dirs = {"__pycache__", ".git", "venv", "env"}

    for dirpath, dirnames, filenames in os.walk(root):

        # фильтр мусора
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        for f in filenames:
            if f.endswith(".py"):
                files.append(os.path.join(dirpath, f))

    return files
'''

    # =========================
    # structure_check.py
    # =========================
    structure = '''def check_structure(files):
    issues = []

    required = ["main.py", "execution.py", "environment.py"]

    found = [f.split("/")[-1] for f in files]

    for r in required:
        if r not in found:
            issues.append(f"❌ Нет файла: {r}")

    if not any("modules" in f for f in files):
        issues.append("❌ Нет папки modules")

    return issues
'''

    # =========================
    # connection_check.py (FIXED)
    # =========================
    connection = '''def check_connections(files):
    issues = []

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()

                # нормальная проверка связей
                if "execution" in content and "decision" not in content:
                    issues.append(f"⚠️ {f}: execution без decision")

                if "decision" in content and "execution" not in content:
                    issues.append(f"⚠️ {f}: decision без execution")

        except:
            continue

    return issues
'''

    # =========================
    # dataflow_check.py (FIXED)
    # =========================
    dataflow = '''def check_dataflow(files):
    issues = []

    required_any = ["data", "goal", "env", "memory", "state"]

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()

                if not any(k in content for k in required_any):
                    issues.append(f"⚠️ {f}: слабый data-flow")

        except:
            continue

    return issues
'''

    # =========================
    # behavior_check.py
    # =========================
    behavior = '''def check_behavior(files):
    issues = []

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()

                if "repeat_count" not in content and "loop" in content:
                    issues.append(f"⚠️ {f}: возможный риск зацикливания")

        except:
            continue

    return issues
'''

    # =========================
    # report.py
    # =========================
    report = '''def generate_report(issues):
    print("\\n📊 META-REPORT:\\n")

    if not issues:
        print("✅ Система стабильна")
        return

    for i in issues:
        print(i)

    print("\\n💡 FIX SUGGESTIONS:")

    if any("execution без decision" in i for i in issues):
        print("→ Связать decision → execution pipeline")

    if any("data-flow" in i for i in issues):
        print("→ Усилить memory/state/data слой")

    if any("зацикливания" in i for i in issues):
        print("→ Добавить анти-loop механизм")
'''

    # =========================
    # observer.py
    # =========================
    observer = '''from scanner import scan_repository
from structure_check import check_structure
from connection_check import check_connections
from dataflow_check import check_dataflow
from behavior_check import check_behavior
from report import generate_report


def run():
    print("🧠 META-OBSERVER START\\n")

    files = scan_repository(".")

    issues = []
    issues += check_structure(files)
    issues += check_connections(files)
    issues += check_dataflow(files)
    issues += check_behavior(files)

    generate_report(issues)


if __name__ == "__main__":
    run()
'''

    # =========================
    # WRITE FILES
    # =========================
    write_file("meta/scanner.py", scanner)
    write_file("meta/structure_check.py", structure)
    write_file("meta/connection_check.py", connection)
    write_file("meta/dataflow_check.py", dataflow)
    write_file("meta/behavior_check.py", behavior)
    write_file("meta/report.py", report)
    write_file("meta/observer.py", observer)

    print("✅ Meta-Observer установлен!")
    print("🚀 run: python meta/observer.py")


if __name__ == "__main__":
    setup_meta_observer()
