import os
import json


# =========================
# 📦 LOAD ARCHITECTURE
# =========================
def load_architecture():
    if not os.path.exists("megabot_architecture.json"):
        return None
    try:
        with open("megabot_architecture.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


# =========================
# 🔁 CORE LOOP CHECK
# =========================
def check_core(data, arch):
    data.setdefault("log", [])

    if "last_layer" not in data:
        data["log"].append("⚠️ doctor: no layer tracking")


# =========================
# 🧠 MAIN DOCTOR
# =========================
def doctor(data):
    data.setdefault("log", [])
    issues = []

    # =========================
    # 💾 MEMORY CHECK
    # =========================
    if not os.path.exists("memory.json"):
        issues.append("memory_missing")
        try:
            with open("memory.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            data["log"].append("🛠 doctor: memory.json created")
        except Exception as e:
            data["log"].append(f"❌ doctor memory error: {e}")

    # =========================
    # 📦 ARCHITECTURE CHECK
    # =========================
    arch = load_architecture()

    if arch:
        # проверка модулей
        required = arch.get("required_modules", [])
        for mod in required:
            path = f"modules/{mod}.py"
            if not os.path.exists(path):
                issues.append(f"missing_{mod}")
                data["log"].append(f"❌ missing module: {mod}")

        # проверка ядра (минимальная)
        check_core(data, arch)

    else:
        issues.append("no_architecture")
        data["log"].append("⚠️ doctor: no architecture file")

    # =========================
    # 🧠 EXPERIENCE CHECK
    # =========================
    if not data.get("experience"):
        data["log"].append("⚠️ doctor: no experience yet")

    # =========================
    # 📊 RESULT
    # =========================
    if issues:
        data["log"].append(f"⚠️ doctor issues: {issues}")
    else:
        data["log"].append("✅ doctor: system OK")

    data["doctor_issues"] = issues

    return data
