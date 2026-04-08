import os
import json
import subprocess
import time

LOG_FILE = "run_log.txt"


# =========================
# 🚀 ЗАПУСК МЕГАБОТА
# =========================
def run_bot():
    try:
        result = subprocess.run(
            ["python", "main.py", "развивай себя"],
            capture_output=True,
            text=True
        )

        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(result.stdout)

        return result.stdout

    except Exception as e:
        print("Run error:", e)
        return ""


# =========================
# 🔍 АНАЛИЗ ЛОГА
# =========================
def analyze_log(text):
    issues = []

    if "generate_idea" in text and "create_module" not in text:
        issues.append("NO_MODULE_CREATION")

    if "experience': []" in text:
        issues.append("NO_EXPERIENCE")

    if "module created" not in text and "create_module" in text:
        issues.append("CREATE_NOT_EXECUTED")

    return issues


# =========================
# 🔧 ФИКС: execution.py
# =========================
def fix_execution():
    if not os.path.exists("execution.py"):
        return False

    with open("execution.py", "r", encoding="utf-8") as f:
        code = f.read()

    if "FORCE_CREATE_MODULE" in code:
        return True  # уже фиксили

    fix_code = """
# 🔥 FORCE CREATE MODULE IF NONE EXISTS
if not data.get("experience"):
    data["decision"] = "create_module"
"""

    code = fix_code + "\n" + code

    with open("execution.py", "w", encoding="utf-8") as f:
        f.write(code)

    print("FIXED: execution.py")
    return True


# =========================
# 🔧 ФИКС: decision.py
# =========================
def fix_decision():
    if not os.path.exists("decision.py"):
        return False

    with open("decision.py", "r", encoding="utf-8") as f:
        code = f.read()

    if "FORCE_BOOTSTRAP_FIX" in code:
        return True

    fix_code = """
# 🔥 FORCE BOOTSTRAP FIX
if data.get("analysis") == "bootstrap" and not data.get("experience"):
    data["decision"] = "create_module"
"""

    code = code + "\n" + fix_code

    with open("decision.py", "w", encoding="utf-8") as f:
        f.write(code)

    print("FIXED: decision.py")
    return True


# =========================
# 🔄 ГЛАВНЫЙ ЦИКЛ
# =========================
def main():
    for i in range(3):
        print(f"\n=== RUN {i+1} ===")

        output = run_bot()
        issues = analyze_log(output)

        print("Issues:", issues)

        if not issues:
            print("✅ SYSTEM OK")
            break

        if "NO_MODULE_CREATION" in issues:
            fix_execution()

        if "CREATE_NOT_EXECUTED" in issues:
            fix_decision()

        time.sleep(1)


if __name__ == "__main__":
    main()
