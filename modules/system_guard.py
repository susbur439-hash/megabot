def system_guard(data):
    # =========================
    # 🧠 INIT
    # =========================

    if "log" not in data:
        data["log"] = []

    if "errors" not in data:
        data["errors"] = []

    if "fail_count" not in data:
        data["fail_count"] = 0

    # =========================
    # 🔍 DETECT FAIL
    # =========================

    success = data.get("success", True)

    if not success:
        data["fail_count"] += 1

        error_info = {
            "layer": data.get("last_layer", "unknown"),
            "decision": data.get("decision"),
            "cycle_fail": data["fail_count"]
        }

        data["errors"].append(error_info)

        data["log"].append(f"❌ error in {error_info['layer']}")

    else:
        data["fail_count"] = 0

    # =========================
    # 🧠 SMART CONTROL
    # =========================

    if data["fail_count"] >= 2:
        data["mode"] = "fix"
        data["force_explore"] = True
        data["log"].append("🧠 guard: switch to FIX mode")

    if data.get("repeat_count", 0) >= 3:
        data["force_explore"] = True
        data["log"].append("🔁 guard: anti-loop activated")

    if len(data["log"]) > 100:
        data["log"] = data["log"][-50:]
        data["log"].append("🧹 guard: log cleanup")

    # =========================
    # 📈 PROGRESS CHECK
    # =========================

    score = data.get("evaluation", {}).get("score", 0)

    if score < 40:
        data["mode"] = "fix"
        data["log"].append("📉 guard: low score → FIX")

    elif score > 85:
        data["mode"] = "balanced"
        data["log"].append("📈 guard: stable growth")

    return data
