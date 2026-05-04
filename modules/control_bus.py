# =========================
# 🧠 MEGABOT CONTROL BUS v2 (MAX)
# =========================

import time
import json
from collections import deque


class ControlBus:

    def __init__(self, memory_limit=500):

        # =========================
        # 🧠 CORE STATE
        # =========================
        self.state = {
            "mode": "normal",
            "phase": "init",
            "trend": "stable",
            "energy": 100,
            "cycle": 0,
            "health": 100,
            "stability": 1.0,
        }

        # =========================
        # 📡 SIGNAL STREAM
        # =========================
        self.signals = deque(maxlen=memory_limit)

        # =========================
        # 🧠 EXPERIENCE MEMORY
        # =========================
        self.memory = deque(maxlen=memory_limit)

        # =========================
        # 📊 METRICS
        # =========================
        self.metrics = {
            "success": 0,
            "fail": 0,
            "create": 0,
            "run": 0,
        }

        # =========================
        # ⚙ CONTROL FLAGS
        # =========================
        self.flags = {
            "loop_detected": False,
            "stagnation": False,
            "overcreate": False,
        }

    # =========================
    # 📡 EMIT SIGNAL
    # =========================
    def emit(self, signal: dict):
        if not isinstance(signal, dict):
            return

        signal = signal.copy()
        signal["ts"] = time.time()

        self.signals.append(signal)

        action = signal.get("action")

        if action == "create_module":
            self.metrics["create"] += 1

        elif action == "run_module":
            self.metrics["run"] += 1

        if signal.get("result") == "success":
            self.metrics["success"] += 1

        if signal.get("result") == "fail":
            self.metrics["fail"] += 1

        self._detect_anomalies()

    # =========================
    # 🧠 UPDATE STATE
    # =========================
    def update(self, patch: dict):
        if not isinstance(patch, dict):
            return

        for k, v in patch.items():
            self.state[k] = v

    # =========================
    # 📊 ANALYTICS CORE
    # =========================
    def get_bias(self):

        return {
            "create": self.metrics["create"],
            "run": self.metrics["run"],
            "success": self.metrics["success"],
            "fail": self.metrics["fail"],
        }

    # =========================
    # 🔁 FEEDBACK LOOP
    # =========================
    def feedback(self):

        bias = self.get_bias()

        # 🧠 energy model
        if bias["success"] > bias["fail"]:
            self.state["energy"] = min(100, self.state["energy"] + 1)
        else:
            self.state["energy"] = max(0, self.state["energy"] - 1)

        # 📊 trend
        if bias["create"] > bias["run"] * 1.5:
            self.state["trend"] = "create_overflow"
        elif bias["run"] > bias["create"] * 1.5:
            self.state["trend"] = "run_stable"
        else:
            self.state["trend"] = "balanced"

        # 🧠 stability
        total = max(1, len(self.signals))
        success_rate = bias["success"] / total

        self.state["stability"] = round(success_rate, 3)

        self.state["cycle"] += 1

        return {
            "state": self.state,
            "bias": bias,
            "flags": self.flags,
        }

    # =========================
    # 🚨 ANOMALY DETECTION
    # =========================
    def _detect_anomalies(self):

        if self.metrics["create"] > self.metrics["run"] * 3:
            self.flags["overcreate"] = True

        if len(self.signals) > 50:
            recent = list(self.signals)[-50:]

            creates = sum(1 for s in recent if s.get("action") == "create_module")

            if creates > 40:
                self.flags["loop_detected"] = True
            else:
                self.flags["loop_detected"] = False

    # =========================
    # 🧠 MEMORY STORE
    # =========================
    def remember(self, data: dict):
        if isinstance(data, dict):
            self.memory.append({
                "ts": time.time(),
                "data": data
            })

    # =========================
    # 🔌 INJECT INTO SYSTEM
    # =========================
    def inject(self, data: dict):

        if not isinstance(data, dict):
            data = {}

        data["control_state"] = self.state.copy()
        data["control_bias"] = self.get_bias()
        data["control_flags"] = self.flags.copy()

        return data

    # =========================
    # 💾 EXPORT STATE
    # =========================
    def export(self, path="control_bus_dump.json"):

        dump = {
            "state": self.state,
            "metrics": self.metrics,
            "flags": self.flags,
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dump, f, indent=2, ensure_ascii=False)
        except:
            pass


# =========================
# 🌐 SINGLETON
# =========================
CONTROL_BUS = ControlBus()


# =========================
# 🚀 API
# =========================
def emit(signal: dict):
    return CONTROL_BUS.emit(signal)


def update_state(patch: dict):
    return CONTROL_BUS.update(patch)


def feedback():
    return CONTROL_BUS.feedback()


def remember(data: dict):
    return CONTROL_BUS.remember(data)


def inject(data: dict):
    return CONTROL_BUS.inject(data)


def export():
    return CONTROL_BUS.export()
