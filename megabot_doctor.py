import os
import json
import traceback

print("\n=== 🧠 MEGABOT DOCTOR v1.0 ===\n")

issues = []

# =========================
# 📁 FILE CHECK
# =========================
print("📁 FILE CHECK")

if not os.path.exists("modules"):
    issues.append("❌ Нет папки modules")

if not os.path.exists("main.py"):
    issues.append("❌ Нет main.py")

if os.path.exists("memory.json"):
    print("✅ memory.json найден")
else:
    print("❌ memory.json отсутствует")
    issues.append("memory_missing")

print("\n")

# =========================
# 🧩 MODULE IMPORT CHECK
# =========================
print("🧩 MODULE IMPORT CHECK")

required = [
    ("modules.analysis", "analysis"),
    ("modules.decision", "decision"),
    ("modules.execution", "execution"),
    ("modules.goals", "set_goal"),
    ("modules.system_guard", "system_guard"),
    ("modules.self_improver", "self_improver"),
]

for mod, func in required:
    try:
        module = __import__(mod, fromlist=[func])
        if hasattr(module, func):
            print(f"✅ {mod}.{func}")
        else:
            print(f"❌ {mod} нет функции {func}")
            issues.append(f"{mod}_missing_func")
    except Exception as e:
        print(f"❌ {mod} не импортируется")
        issues.append(f"{mod}_import_error")

print("\n")

# =========================
# 🔥 EXECUTION TEST
# =========================
print("🔥 EXECUTION TEST")

try:
    from modules.execution import execution

    test_data = {
        "goal": {"progress": 0},
        "log": [],
        "memory": [],
        "experience": []
    }

    before = test_data["goal"]["progress"]

    result = execution(test_data)

    after = result["goal"]["progress"]

    print(f"progress: {before} → {after}")

    if after <= before:
        print("⚠️ execution НЕ увеличивает прогресс")
        issues.append("execution_no_progress")
    else:
        print("✅ execution OK")

except Exception as e:
    print("❌ execution CRASH")
    traceback.print_exc()
    issues.append("execution_crash")

print("\n")

# =========================
# 💾 MEMORY SAVE TEST
# =========================
print("💾 MEMORY SAVE TEST")

test_data = {"test": True}

try:
    from modules.execution import save_to_memory
    save_to_memory(test_data)

    if os.path.exists("memory.json"):
        print("✅ memory.json создаётся")
    else:
        print("❌ memory.json НЕ создаётся")
        issues.append("memory_not_created")

except Exception as e:
    print("❌ save_to_memory ошибка")
    issues.append("memory_save_error")

print("\n")

# =========================
# 💾 MEMORY LOAD TEST
# =========================
print("💾 MEMORY LOAD TEST")

if os.path.exists("memory.json"):
    try:
        with open("memory.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ memory.json читается")
    except:
        print("❌ memory.json повреждён")
        issues.append("memory_corrupted")

print("\n")

# =========================
# 🔁 LOOP DETECTION
# =========================
print("🔁 LOOP DETECTION")

if os.path.exists("memory.json"):
    try:
        with open("memory.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        memory = data.get("memory", [])

        if len(memory) >= 5:
            last = memory[-5:]
            if len(set(last)) == 1:
                print(f"⚠️ LOOP DETECTED: {last[0]}")
                issues.append("loop_detected")
            else:
                print("✅ loop нет")
        else:
            print("ℹ️ мало данных")

    except:
        print("❌ ошибка чтения памяти")

print("\n")

# =========================
# 🧠 FINAL DIAGNOSIS
# =========================
print("=== 🧠 FINAL DIAGNOSIS ===\n")

if not issues:
    print("✅ СИСТЕМА ЗДОРОВА")
else:
    print("❌ НАЙДЕНЫ ПРОБЛЕМЫ:\n")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")

    print("\n=== 🛠 РЕКОМЕНДАЦИИ ===")

    for issue in issues:
        if issue == "memory_missing":
            print("- memory.json не создаётся → проблема в save_to_memory")

        elif issue == "memory_not_created":
            print("- save_to_memory не работает → путь или вызов")

        elif issue == "execution_no_progress":
            print("- execution не влияет на goal → логика модуля")

        elif issue == "execution_crash":
            print("- execution падает → критическая ошибка")

        elif issue == "loop_detected":
            print("- система зациклилась → проблема в decision/strategy")

        elif "import" in issue:
            print("- проблема с импортами модулей")

print("\n=== END ===")
