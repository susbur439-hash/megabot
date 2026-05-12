import json
import os
from collections import defaultdict

class CentralBrainV2:
    """
    🧠 Megabot Central Brain v2

    Главная цель:
    - контроль архитектуры
    - обнаружение хаоса
    - запуск self-repair
    - анализ состояния системы
    """

    def __init__(self, brain_map_path="brain_map.json"):
        self.brain_map_path = brain_map_path
        self.brain_map = self.load_brain_map()

        self.state = {
            "chaos_level": 0,
            "overloaded_layers": [],
            "risk_modules": [],
            "health_score": 100
        }

    # =========================
    # 📥 LOAD
    # =========================
    def load_brain_map(self):
        if not os.path.exists(self.brain_map_path):
            return {}

        with open(self.brain_map_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # =========================
    # 🧠 ANALYZE SYSTEM
    # =========================
    def analyze(self):
        layers = self.brain_map.get("layers", {})

        overload_threshold = 200  # условный лимит модулей
        chaos_score = 0

        overloaded = []

        for layer_name, modules in layers.items():
            if len(modules) > overload_threshold:
                overloaded.append(layer_name)
                chaos_score += 20

        # orphan detection
        orphans = self.brain_map.get("orphans", [])
        if len(orphans) > 0:
            chaos_score += len(orphans) * 2

        # risk evaluation
        risk_modules = self.detect_risk_modules()

        self.state["chaos_level"] = chaos_score
        self.state["overloaded_layers"] = overloaded
        self.state["risk_modules"] = risk_modules
        self.state["health_score"] = max(0, 100 - chaos_score)

        return self.state

    # =========================
    # ⚠ RISK DETECTION
    # =========================
    def detect_risk_modules(self):
        imports = self.brain_map.get("imports", {})

        risk = []

        for file, deps in imports.items():
            if len(deps) > 15:  # слишком много зависимостей
                risk.append({
                    "file": file,
                    "reason": "high_dependency_load"
                })

        return risk

    # =========================
    # 🔥 DECISION ENGINE
    # =========================
    def decide_action(self):
        if self.state["chaos_level"] > 50:
            return "EMERGENCY_REPAIR"

        if self.state["health_score"] < 70:
            return "OPTIMIZE_ARCHITECTURE"

        if len(self.state["risk_modules"]) > 10:
            return "REFACTOR_MODULES"

        return "NORMAL"

    # =========================
    # 🔧 EXECUTION SIGNAL
    # =========================
    def run_cycle(self):
        self.analyze()
        action = self.decide_action()

        return {
            "state": self.state,
            "action": action
        }


# =========================
# 🚀 ENTRYPOINT
# =========================
def run_central_brain():
    brain = CentralBrainV2()
    result = brain.run_cycle()

    print("🧠 CENTRAL BRAIN v2 REPORT")
    print(json.dumps(result, indent=2))

    return result


if __name__ == "__main__":
    run_central_brain()
