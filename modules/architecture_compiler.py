import json
import os

# =========================
# 🧠 ARCHITECTURE COMPILER
# =========================

ARCH_FILE = "architecture.json"
MODULES_DIR = "modules"


def load_architecture():

    if not os.path.exists(ARCH_FILE):
        return None

    with open(ARCH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def scan_modules():

    if not os.path.exists(MODULES_DIR):
        return []

    return [
        f.replace(".py", "")
        for f in os.listdir(MODULES_DIR)
        if f.endswith(".py")
    ]


def compile_architecture(arch):

    required = arch.get("required_modules", [])
    existing = scan_modules()

    missing = []
    extra = []

    for m in required:
        if m not in existing:
            missing.append(m)

    for m in existing:
        if m not in required:
            extra.append(m)

    return {
        "required": required,
        "existing": existing,
        "missing": missing,
        "extra": extra
    }


def build_plan(report):

    plan = {
        "create": report["missing"],
        "review": report["extra"],
        "status": "ok" if not report["missing"] else "incomplete"
    }

    return plan


def run(task=None):

    arch = load_architecture()

    if not arch:
        return {
            "status": "error",
            "message": "architecture.json not found"
        }

    report = compile_architecture(arch)
    plan = build_plan(report)

    return {
        "task": "architecture_compile",
        "report": report,
        "plan": plan,
        "log": [
            f"missing={len(report['missing'])}",
            f"extra={len(report['extra'])}"
        ]
    }
