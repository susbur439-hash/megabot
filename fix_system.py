import os

# =========================
# 📌 ФАЙЛЫ ДЛЯ ФИКСА
# =========================
FILES = [
    "decision.py",
    "execution.py",
    "main.py"
]

# =========================
# 🔧 ЗАМЕНЫ
# =========================
REPLACEMENTS = {
    "create_module": "add_module",
}

# =========================
# 🔄 ФИКС ФАЙЛА
# =========================
def fix_file(path):
    if not os.path.exists(path):
        print(f"❌ {path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 🔥 замены
    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)

    # =========================
    # 🔥 ДОБАВЛЯЕМ NORMALIZER (если нет)
    # =========================
    if "normalize_action" not in content and "decision" in path:
        content = "from core.actions import normalize_action\n" + content

        content = content.replace(
            "return data",
            "    data['decision'] = normalize_action(data.get('decision'))\n    return data"
        )

    if "normalize_action" not in content and "execution" in path:
        content = "from core.actions import normalize_action\n" + content

        content = content.replace(
            "decision = data.get(\"decision\")",
            "decision = normalize_action(data.get(\"decision\"))"
        )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ fixed {path}")


# =========================
# 📁 СОЗДАЁМ core/actions.py
# =========================
def create_actions():
    os.makedirs("core", exist_ok=True)

    code = """# =========================
# 🎯 ACTION STANDARD
# =========================

ACTIONS = {
    "IDEA": "generate_idea",
    "ADD": "add_module",
    "RUN": "run_module",
    "IMPROVE": "improve_module"
}

def normalize_action(action: str) -> str:
    if not action:
        return ACTIONS["IDEA"]

    action = action.lower().strip()

    mapping = {
        "create_module": ACTIONS["ADD"],
        "add_module": ACTIONS["ADD"],
        "run_module": ACTIONS["RUN"],
        "improve_module": ACTIONS["IMPROVE"],
        "generate_idea": ACTIONS["IDEA"],
    }

    return mapping.get(action, ACTIONS["IDEA"])
"""

    with open("core/actions.py", "w", encoding="utf-8") as f:
        f.write(code)

    print("✅ created core/actions.py")


# =========================
# 🚀 RUN
# =========================
def main():
    create_actions()

    for file in FILES:
        fix_file(file)

    print("\n🔥 SYSTEM NORMALIZED")


if __name__ == "__main__":
    main()
