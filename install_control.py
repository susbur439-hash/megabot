import os

# =========================
# CREATE FILE SAFE
# =========================
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True) if "/" in path else None

    if os.path.exists(path):
        print(f"⚠️ {path} уже существует, пропущен")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ создан: {path}")


# =========================
# RUN CONTROL
# =========================
run_control_code = '''import subprocess
import os

def interpret_task(task):
    t = task.lower()

    if "meta/" in t:
        return {"type": "tool", "action": "external", "reason": "system tool"}

    if "проверь" in t or "анализ" in t:
        return {"type": "analysis", "action": "observer"}

    if "исправь" in t or "почини" in t:
        return {"type": "diagnostics", "action": "doctor"}

    return {"type": "development", "action": "execute"}


def run_megabot(task):
    subprocess.run(["python", "main.py", task])


def run_observer():
    subprocess.run(["python", "meta/observer.py"])


def run_doctor():
    subprocess.run(["python", "meta/doctor.py"])


def main():
    task = input("Введите задачу: ")

    info = interpret_task(task)

    print("\\n=== CONTROL REPORT ===")
    print(f"📌 Тип: {info['type']}")

    if info["action"] == "external":
        print("⚠️ Внешний инструмент")
        print("👉 Запусти вручную:")
        print(f"python {task}")
        return

    if info["action"] == "observer":
        print("🔍 Запуск Observer")
        run_observer()
        return

    if info["action"] == "doctor":
        print("🛠 Запуск Doctor")
        run_doctor()
        return

    print("🚀 Запуск Megabot")
    run_megabot(task)


if __name__ == "__main__":
    main()
'''


# =========================
# OBSERVER
# =========================
observer_code = '''import os

def scan_project():
    report = []
    report.append("=== OBSERVER REPORT ===")

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                report.append(f"📄 {path}")

    return report


def main():
    report = scan_project()
    for line in report:
        print(line)


if __name__ == "__main__":
    main()
'''


# =========================
# DOCTOR
# =========================
doctor_code = '''import os

def check_structure():
    report = []
    report.append("=== DOCTOR REPORT ===")

    required = [
        "main.py",
        "execution.py",
        "environment.py",
        "modules"
    ]

    for item in required:
        if os.path.exists(item):
            report.append(f"✔ {item}")
        else:
            report.append(f"❌ {item} отсутствует")

    return report


def main():
    report = check_structure()
    for line in report:
        print(line)


if __name__ == "__main__":
    main()
'''


# =========================
# INSTALL
# =========================
write_file("run_control.py", run_control_code)
write_file("meta/observer.py", observer_code)
write_file("meta/doctor.py", doctor_code)

print("\\n🚀 Control Layer установлен")
