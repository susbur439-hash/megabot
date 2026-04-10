import os


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def setup_meta_observer():
    print("🧠 Установка Meta-Observer...\n")

    # =========================
    # scanner.py
    # =========================
    scanner = '''import os

def scan_repository(root="."):
    files = []

    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
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
    # connection_check.py
    # =========================
    connection = '''def check_connections(files):
    issues = []

    for f in files:
        if not f.endswith(".py"):
            continue

        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()

                if "execution(" in content and "decision" not in content:
                    issues.append(f"⚠️ {f}: execution без decision")

        except:
            pass

    return issues
'''

    # =========================
    # dataflow_check.py
    # =========================
    dataflow = '''def check_dataflow(files):
    issues = []

    keywords = ["data[", "goal", "env", "experience"]

    for f in files:
        if not f.endswith(".py"):
            continue

        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()

                if not any(k in content for k in keywords):
                    issues.append(f"⚠️ {f}: нет работы с data")

        except:
            pass

    return issues
'''

    # =========================
    # behavior_check.py
    # =========================
    behavior = '''def check_behavior(files):
    issues = []

    for f in files:
        if not f.endswith(".py"):
            continue

        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()

                if "repeat_count" not in content:
                    issues.append(f"⚠️ {f}: нет анти-лупа")

        except:
            pass

    return issues
'''

    # =========================
    # report.py
    # =========================
    report = '''def generate_report(issues):
    print("\\n📊 ОТЧЁТ:\\n")

    if not issues:
        print("✅ Всё выглядит нормально")
        return

    for i in issues:
        print(i)

    print("\\n💡 Рекомендации:")

    if any("Нет файла" in i for i in issues):
        print("👉 Восстановить базовые файлы")

    if any("execution без decision" in i for i in issues):
        print("👉 Связать decision → execution")

    if any("нет анти-лупа" in i for i in issues):
        print("👉 Добавить repeat_count")

    if any("нет работы с data" in i for i in issues):
        print("👉 Проверить data flow")
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
    print("🧠 META-OBSERVER ЗАПУЩЕН\\n")

    files = scan_repository()

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

    print("✅ Meta-Observer установлен!\n")
    print("🚀 Запуск:")
    print("python meta/observer.py")


if __name__ == "__main__":
    setup_meta_observer()
