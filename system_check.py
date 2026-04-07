import os
import json

print("🔍 MEGABOT FULL SYSTEM AUDIT\n")

# =========================
# 📁 FULL DIRECTORY TREE
# =========================
print("📁 FULL STRUCTURE:\n")

total_files = 0
total_dirs = 0

for root, dirs, files in os.walk("."):
    level = root.count(os.sep)
    indent = "  " * level
    print(f"{indent}📂 {root}")

    total_dirs += len(dirs)

    for f in files:
        total_files += 1
        path = os.path.join(root, f)

        try:
            size = os.path.getsize(path)
        except:
            size = 0

        size_kb = round(size / 1024, 2)

        flag = ""
        if size == 0:
            flag = " ⚠️ EMPTY"

        print(f"{indent}  📄 {f} ({size_kb} KB){flag}")

print("\n========================")
print(f"📊 Всего папок: {total_dirs}")
print(f"📊 Всего файлов: {total_files}")

# =========================
# 🔍 PYTHON ANALYSIS
# =========================
print("\n🐍 PYTHON FILE ANALYSIS:\n")

execution_count = 0
decision_map = {}
errors = []

keywords = [
    "generate_idea",
    "create_module",
    "add_module",
    "run_module",
    "improve_module"
]

for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)

            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()

                # execution
                if "def execution(" in content:
                    execution_count += 1
                    print(f"⚠️ execution() найден: {path}")

                # decisions
                for k in keywords:
                    if k in content:
                        decision_map.setdefault(k, []).append(path)

                # подозрительные места
                if "except:" in content:
                    errors.append((path, "bare except"))

                if "pass" in content and "except" in content:
                    errors.append((path, "silent error pass"))

            except Exception as e:
                print(f"❌ Ошибка чтения: {path}")

print("\n========================")
print(f"⚠️ execution() всего: {execution_count}")

# =========================
# 🔍 DECISION MAP
# =========================
print("\n🧠 DECISION MAP:\n")

for k, files in decision_map.items():
    print(f"🔹 {k}:")
    for f in files:
        print("   -", f)

# =========================
# 📦 MODULES CHECK
# =========================
print("\n📦 MODULES CHECK:\n")

if os.path.exists("modules"):
    modules = [f for f in os.listdir("modules") if f.endswith(".py")]
    print(f"Найдено модулей: {len(modules)}")

    if not modules:
        print("❌ ПРОБЛЕМА: модулей нет → система не развивается")

    for m in modules[:20]:
        print(" -", m)
else:
    print("❌ Папка modules отсутствует")

# =========================
# 💾 MEMORY ANALYSIS
# =========================
print("\n💾 MEMORY ANALYSIS:\n")

if os.path.exists("memory.json"):
    try:
        with open("memory.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        print("✔ memory.json найден")

        mem = data.get("memory", [])
        exp = data.get("experience", [])

        print(f" - memory: {len(mem)}")
        print(f" - experience: {len(exp)}")

        if len(exp) == 0:
            print("❌ ПРОБЛЕМА: опыт не сохраняется")

        if len(mem) > 0:
            print("\n🧠 Последние решения:")
            for d in mem[-10:]:
                print(" -", d)

        print("\n🎯 GOAL:")
        print(data.get("goal"))

    except Exception as e:
        print("❌ Ошибка чтения memory:", e)
else:
    print("❌ memory.json отсутствует")

# =========================
# ⚠️ ERROR SUMMARY
# =========================
print("\n⚠️ POTENTIAL ERRORS:\n")

if errors:
    for e in errors:
        print(f" - {e[0]} → {e[1]}")
else:
    print("✔ критических ошибок не найдено")

print("\n========================")
print("\n✅ FULL AUDIT COMPLETE")
