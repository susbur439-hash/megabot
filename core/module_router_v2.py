import importlib
import os
import json
import traceback
from collections import defaultdict

from core.system_state import system_state

# =========================
# ⚙️ LOG CONTROL
# =========================

LOG_LEVEL = "ERROR"


def log(msg, level="INFO"):
    if LOG_LEVEL == "SILENT":
        return
    if LOG_LEVEL == "ERROR" and level != "ERROR":
        return
    if LOG_LEVEL == "INFO" and level == "DEBUG":
        return
    print(msg)


# =========================
# 🧠 REGISTRY
# =========================

try:
    from modules.system_registry import register_module
except Exception:
    register_module = None


# =========================
# 🧠 ROLE MAP
# =========================

ROLE_MAP = {
    "ENTRYPOINT": ["main", "app", "start", "bot_start"],
    "CONTROL": ["control", "router", "panel", "gateway"],
    "DECISION": ["decision", "brain", "controller"],
    "EXECUTION": ["execution", "executor", "action", "run"],
    "ANALYSIS": ["analysis", "analyzer", "scan"],
    "MEMORY": ["memory", "snapshot", "storage"],
    "LEARNING": ["learn", "learning", "adaptive"]
}


# =========================
# 🧠 ROUTER V2 (v13 LEARNING CORE)
# =========================

class ModuleRouterV2:

    def __init__(self):

        self.modules = {}
        self.roles = defaultdict(list)

        # 🧠 LEARNING STATE
        self.module_score = {}
        self.success_memory = defaultdict(int)
        self.fail_memory = defaultdict(int)

        self.failed = {}

        self.load_modules()
        self.build_architecture_map()

    # =========================
    # 📦 LOAD MODULES
    # =========================

    def load_modules(self):

        path = "modules"

        log("[RouterV2] loading modules...", "INFO")

        if not os.path.exists(path):
            log("[RouterV2] modules folder missing", "ERROR")
            return

        for file in os.listdir(path):

            if not file.endswith(".py") or file.startswith("__"):
                continue

            name = file[:-3]

            try:
                module = importlib.import_module(f"modules.{name}")
                importlib.reload(module)

                if not hasattr(module, "run"):
                    self.failed[name] = "NO_RUN"
                    continue

                self.modules[name] = module

                # 🧠 initial learning weight
                self.module_score[name] = 1.0

                if register_module:
                    try:
                        register_module(name, module)
                    except:
                        pass

            except Exception as e:
                self.failed[name] = str(e)

    # =========================
    # 🧠 ROLE DETECTION
    # =========================

    def detect_role(self, name: str):

        lower = name.lower()

        for role, keys in ROLE_MAP.items():
            for k in keys:
                if k in lower:
                    return role

        return "UNKNOWN"

    # =========================
    # 🧠 ARCH MAP
    # =========================

    def build_architecture_map(self):

        self.roles = defaultdict(list)

        for name in self.modules:
            role = self.detect_role(name)
            self.roles[role].append(name)

        try:
            with open("architecture_map.json", "w", encoding="utf-8") as f:
                json.dump(dict(self.roles), f, indent=2, ensure_ascii=False)
        except:
            pass

    # =========================
    # 🧠 SCORING ENGINE (v13 LEARNING)
    # =========================

    def score_module(self, name, role, state):

        base = self.module_score.get(name, 1.0)

        role_weight = {
            "DECISION": 3,
            "EXECUTION": 3,
            "ANALYSIS": 2,
            "CONTROL": 2,
            "MEMORY": 1.5,
            "ENTRYPOINT": 1,
            "LEARNING": 2
        }.get(role, 1)

        stability = state.get("stability", 1.0)
        energy = state.get("energy", 50)

        learn_bonus = self.success_memory[name] - self.fail_memory[name]

        score = base * role_weight * (0.5 + stability) * (energy / 100)
        score += learn_bonus * 0.1

        return score

    # =========================
    # 🔁 ROUTE (LEARNING VERSION)
    # =========================

    def route(self, command):

        command = self.normalize(command)

        try:
            system_state.load()
            system_state.inject(command)
            state = system_state.get()
        except:
            state = {}

        data = command.get("data", {})

        best_module = None
        best_score = -1

        # 🧠 selection
        for role, modules in self.roles.items():
            for m in modules:

                if m not in self.modules:
                    continue

                score = self.score_module(m, role, state)

                if score > best_score:
                    best_score = score
                    best_module = m

        if not best_module:
            best_module = command.get("module", "director")

        if best_module not in self.modules:
            best_module = "director"

        module = self.modules[best_module]

        try:
            result = module.run({
                **data,
                "system_state": state,
                "roles": dict(self.roles),
                "router_version": "v13-learning",
                "selected_score": best_score
            })

            # =========================
            # 🧠 LEARNING UPDATE
            # =========================

            success = True
            if isinstance(result, dict):
                success = result.get("success", True)

            if success:
                self.success_memory[best_module] += 1
                self.module_score[best_module] *= 1.01
            else:
                self.fail_memory[best_module] += 1
                self.module_score[best_module] *= 0.98

            system_state.update("last_module", best_module)
            system_state.update("last_result", result)

            return {
                "status": "success",
                "module": best_module,
                "score": best_score,
                "learning": {
                    "success": dict(self.success_memory),
                    "fail": dict(self.fail_memory)
                },
                "result": result
            }

        except Exception as e:

            self.fail_memory[best_module] += 1

            return {
                "status": "error",
                "module": best_module,
                "message": str(e),
                "trace": traceback.format_exc()
            }

    # =========================
    # 🧼 NORMALIZE
    # =========================

    def normalize(self, command):

        if isinstance(command, str):
            return {"module": "director", "data": {"task": command}}

        if not isinstance(command, dict):
            return {"module": "director", "data": {"task": str(command)}}

        command.setdefault("data", {})
        command.setdefault("module", "director")

        return command