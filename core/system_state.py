# core/system_state.py

import json
import os

class SystemState:

    def __init__(self):

        self.state = {
            "task": None,
            "brain_map": {},
            "memory": {},
            "modules": {},
            "control": {},
            "experience": [],
            "flags": {},
            "logs": []
        }

    # =========================
    # 📥 LOAD FROM FILES
    # =========================
    def load(self):

        self.state["memory"] = self._load_json("memory.json")
        self.state["brain_map"] = self._load_json("brain_map.json")
        self.state["control"] = self._load_json("control_state.json")

        return self.state

    # =========================
    # 📤 SAVE STATE PARTS
    # =========================
    def save_memory(self):
        self._save_json("memory.json", self.state["memory"])

    # =========================
    # 🔗 UPDATE STATE
    # =========================
    def update(self, key, value):
        self.state[key] = value

    def inject(self, data: dict):
        """
        Главный входной слой
        """
        self.state["task"] = data

        return self.state

    # =========================
    # 📊 GET STATE
    # =========================
    def get(self):
        return self.state

    # =========================
    # 🧠 INTERNAL HELPERS
    # =========================
    def _load_json(self, path):
        if not os.path.exists(path):
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def _save_json(self, path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass


# =========================
# 🚀 SINGLETON INSTANCE
# =========================
system_state = SystemState()
