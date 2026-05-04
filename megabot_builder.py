# =========================
# 🧠 MEGABOT BUILDER v1 (STABLE CORE)
# =========================

import os
import json
import subprocess
from datetime import datetime


# =========================
# 📐 ARCHITECTURE SOURCE OF TRUTH
# =========================
ARCHITECTURE = {
    "core_modules": [
        "director",
        "decision",
        "execution",
        "control_layer",
        "task_interpreter",
        "evaluation",
        "learning",
        "control_bus"
    ],
    "rules": {
        "no_duplicate_create": True,
        "require_run_function": True,
        "max_module_creation_per_cycle": 1,
        "block_create_if_modules_exist": True
    }
}


# =========================
# 🧠 BUILDER CORE
# =========================
class MegabotBuilder:

    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.log = []

    # =========================
    # 🔍 SCAN REPOSITORY
    # =========================
    def scan(self):
        modules = []

        for root, _, files in os.walk(self.repo_path):
            for f in files:
                if f.endswith(".py"):
                    modules.append(f.replace(".py", ""))

        return modules

    # =========================
    # 🧠 CHECK ARCHITECTURE
    # =========================
    def analyze(self, modules):

        missing = []
        existing = set(modules)

        for core in ARCHITECTURE["core_modules"]:
            if core not in existing:
                missing.append(core)

        return {
            "existing": list(existing),
            "missing_core": missing
        }

    # =========================
    # 🧪 RUN TESTS (SAFE)
    # =========================
    def run_tests(self):

        try:
            result = subprocess.run(
                ["pytest", "-q"],
                capture_output=True,
                text=True
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout + result.stderr
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # =========================
    # 🧠 DECIDE FIXES
    # =========================
    def plan(self, analysis, test_result):

        plan = {
            "add": [],
            "fix": [],
            "delete": []
        }

        # ❌ missing core modules
        for m in analysis["missing_core"]:
            plan["add"].append(m)

        # ❌ test fail → safe mode fix
        if not test_result.get("success"):
            plan["fix"].append("review_failed_tests")

        return plan

    # =========================
    # ⚙ APPLY PLAN (SAFE MODE)
    # =========================
    def apply(self, plan):

        # 🚫 safety lock
        if len(plan["add"]) > ARCHITECTURE["rules"]["max_module_creation_per_cycle"]:
            self.log.append("🚫 blocked: too many creations")
            return False

        for module in plan["add"]:
            path = os.path.join(self.repo_path, f"{module}.py")

            if os.path.exists(path):
                continue

            with open(path, "w", encoding="utf-8") as f:
                f.write(f"""
# auto-generated safe module: {module}

def run(data):
    data.setdefault("log", []).append("⚙️ {module} running")
    return data
""")

            self.log.append(f"🧩 created: {module}")

        return True

    # =========================
    # 🚀 RUN CYCLE
    # =========================
    def run(self, data=None):

        self.log.append(f"🚀 cycle start {datetime.now()}")

        modules = self.scan()
        analysis = self.analyze(modules)
        tests = self.run_tests()
        plan = self.plan(analysis, tests)

        self.apply(plan)

        return {
            "analysis": analysis,
            "tests": tests,
            "plan": plan,
            "log": self.log
        }


# =========================
# 🚀 ENTRY POINT
# =========================
if __name__ == "__main__":

    builder = MegabotBuilder()
    result = builder.run()

    print(json.dumps(result, indent=2, ensure_ascii=False))
