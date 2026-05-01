def control(data):

    data.setdefault("log", [])
    data.setdefault("goal", {"progress": 0, "target": 100, "level": 1})
    data.setdefault("env", {})
    data.setdefault("experience", [])

    env = data["env"]
    goal = data["goal"]

    # =========================
    # 🔋 SAFETY
    # =========================
    if env.get("energy", 100) < 20:
        data["mode"] = "safe"

    # =========================
    # 🚀 LEVEL UP
    # =========================
    if goal["progress"] >= goal["target"]:
        goal["level"] += 1
        goal["progress"] = 0
        goal["target"] = int(goal["target"] * 1.2)

        env["energy"] = min(100, env.get("energy", 100) + 10)

        data["log"].append(f"🚀 LEVEL UP → {goal['level']}")

    return data
