import os
import json
import re

print("🔧 MEGABOT AUTO FIX START\n")

# =========================
# 1. MEMORY FIX
# =========================
if not os.path.exists("memory.json"):
    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)
    print("✅ memory.json создан")
else:
    print("✔️ memory.json уже существует")

# =========================
# 2. EXECUTION CHECK
# =========================
print("\n🔍 Проверка execution()...")

execution_files = []

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "def execution" in content:
                        execution_files.append(path)
            except:
                pass

print(f"⚠️ Найдено execution(): {len(execution_files)}")

for f in execution_files:
    print(" -", f)

if len(execution_files) > 1:
    print("\n⚠️ ВНИМАНИЕ: дубли execution()")
    print("👉 Оставь только: modules/execution.py")

# =========================
# 3. MAIN FIX (умный запуск)
# =========================
print("\n🧠 Проверка main.py...")

main_path = "main.py"

if os.path.exists(main_path):
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "Direct run" not in content:
        inject_code = '''

    # 🔥 DIRECT SCRIPT RUN
    if task.endswith(".py") and os.path.exists(task):
        print("🚀 Direct run:", task)
        os.system(f"python {task}")
        exit()
'''

        # вставка перед run(task)
        content = re.sub(r'run\(task\)', inject_code + "\n    run(task)", content)

        with open(main_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ main.py обновлён (direct run добавлен)")
    else:
        print("✔️ main.py уже настроен")
else:
    print("❌ main.py не найден")

print("\n🚀 AUTO FIX COMPLETE")
