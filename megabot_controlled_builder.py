# =========================
# 🧠 MEGABOT CONTROLLED MAX BUILDER v2
# =========================

import os
import subprocess
import json
from datetime import datetime

# =========================
# 📐 TARGET ARCHITECTURE (ЭТАЛОН)
# =========================
ARCH = {
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
        "max_changes_per_cycle": 1,
        "block_if_loop": True,
        "block_if_overcreate": True,
        "require_run_function": True
    }
}


# =========================
# 🧠 BUILDER
# =========================
class ControlledMaxBuilder:

    def __init__(self, repo="."):
        self.repo = repo
        self.log = []

    # =========================
    # 🔍 SCAN REPO
    # =========================
    def scan(self):
        modules = []

        for root, _, files in os.walk(self.repo):
            for f in files:
                if f.endswith(".py"):
                    modules.append(f.replace(".py", ""))

        return modules

    # =========================
    # 📊 ANALYZE ARCH
    # =========================
    def analyze(self, modules):

        existing = set(modules)
        missing = []

        for m in ARCH["core_modules"]:
            if m not in existing:
                missing.append(m)

        return {
            "existing": list(existing),
            "missing": missing
        }

    # =========================
    # 🧠 CONTROL BUS CHECK (optional safe read)
    # =========================
    def read_control_state(self):

        try:
            if os.path.exists("control_bus_dump.json"):
                with open("control_bus_dump.json", "r") as f:
                    return json.load(f)
        except:
            pass

        return {}

    # =========================
    # 🧪 RUN TESTS
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
    # 🚨 DECISION ENGINE
    # =========================
    def decide(self, analysis, control, tests):

        flags = control.get("flags", {}) if isinstance(control, dict) else {}

        # 🚨 SAFETY BLOCKS
        if flags.get("loop_detected"):
            return {"action": "BLOCK", "reason": "loop detected"}

        if flags.get("overcreate"):
            return {"action": "BLOCK", "reason": "overcreate detected"}

        # ❌ tests failed → do nothing risky
        if not tests.get("success"):
            return {"action": "WAIT", "reason": "tests failing"}

        # 🧠 missing core → fix
        if analysis["missing"]:
            return {
                "action": "ADD",
                "targets": analysis["missing"][:ARCH["rules"]["max_changes_per_cycle"]]
            }

        return {"action": "STABLE"}

    # =========================
    # ⚙ APPLY CHANGES
    # =========================
    def apply(self, decision):

        if decision["action"] != "ADD":
            self.log.append(f"🧠 no changes: {decision}")
            return

        for module in decision["targets"]:

            path = os.path.join(self.repo, f"{module}.py")

            if os.path.exists(path):
                continue

            with open(path, "w", encoding="utf-8") as f:
                f.write(f"""
# auto-generated core module: {module}

def run(data):
    data.setdefault("log", []).append("⚙️ {module} active")
    return data
""")

            self.log.append(f"🧩 created: {module}")

    # =========================
    # 🚀 RUN CYCLE
    # =========================
    def run(self):

        self.log.append(f"🚀 cycle start {datetime.now()}")

        modules = self.scan()
        analysis = self.analyze(modules)
        control = self.read_control_state()
        tests = self.run_tests()

        decision = self.decide(analysis, control, tests)
        self.apply(decision)

        return {
            "analysis": analysis,
            "decision": decision,
            "tests": tests,
            "log": self.log
        }


# =========================
# 🚀 ENTRY POINT
# =========================
if __name__ == "__main__":

    builder = ControlledMaxBuilder()
    result = builder.run()

    print(json.dumps(result, indent=2, ensure_ascii=False))
