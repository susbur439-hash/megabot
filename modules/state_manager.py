import time


# =========================
# 🧠 STATE INIT
# =========================
def init_state(data):
    state = data.setdefault("state", {})

    state.setdefault("created_at", time.time())
    state.setdefault("cycles", 0)

    state.setdefault("mode", "explore")  # explore / exploit / improve
    state.setdefault("phase", "normal")  # normal / stagnation / crisis

    state.setdefault("focus", "growth")  # growth / stability / recovery

    state.setdefault("last_action", None)
    state.setdefault("last_result", None)

    state.setdefault("score_trend", [])
    state.setdefault("progress_trend", [])

    return data


# =========================
# 📊 UPDATE STATE
# =========================
def update_state(data):
    state = data["state"]
    env = data.get("env", {})
    goal = data.get("goal", {})

    state["cycles"] += 1

    progress = goal.get("progress", 0)
    entropy = env.get("entropy", 0)

    # 📈 обновляем тренды
    state["progress_trend"].append(progress)
    state["progress_trend"] = state["progress_trend"][-10:]

    # 📉 анализ тренда
    if len(state["progress_trend"]) >= 3:
        a, b, c = state["progress_trend"][-3:]
        if c > b > a:
            trend = "up"
        elif c < b < a:
            trend = "down"
        else:
            trend = "stable"
    else:
        trend = "stable"

    state["trend"] = trend

    # ⚠️ стагнация
    stagnation = trend == "stable"
    state["stagnation"] = stagnation

    # 🔥 кризис
    if entropy > 15 or trend == "down":
        state["phase"] = "crisis"
    elif stagnation:
        state["phase"] = "stagnation"
    else:
        state["phase"] = "normal"

    return data


# =========================
# 🧠 DECIDE MODE
# =========================
def decide_mode(data):
    state = data["state"]

    if state["phase"] == "crisis":
        state["mode"] = "explore"

    elif state["phase"] == "stagnation":
        state["mode"] = "improve"

    elif state["trend"] == "up":
        state["mode"] = "exploit"

    else:
        state["mode"] = "explore"

    return data


# =========================
# 🎯 SET FOCUS
# =========================
def set_focus(data):
    state = data["state"]
    env = data.get("env", {})

    energy = env.get("energy", 100)

    if energy < 30:
        state["focus"] = "recovery"
    elif state["mode"] == "exploit":
        state["focus"] = "growth"
    elif state["mode"] == "improve":
        state["focus"] = "stability"
    else:
        state["focus"] = "growth"

    return data


# =========================
# 🧠 MAIN ENTRY
# =========================
def run(data):
    data = init_state(data)
    data = update_state(data)
    data = decide_mode(data)
    data = set_focus(data)

    data["log"].append(
        f"🧠 state: mode={data['state']['mode']} | phase={data['state']['phase']} | trend={data['state']['trend']}"
    )

    return data
