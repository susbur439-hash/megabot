# =========================
# 🧠 SELF IMPROVER
# =========================

def self_improver(data):
    data.setdefault("log", [])
    data.setdefault("experience", [])
    data.setdefault("errors", [])

    # =========================
    # 🔍 АНАЛИЗ ОШИБОК
    # =========================

    errors = data.get("errors", [])

    if errors:
        last_error = errors[-1]
        layer = last_error.get("layer", "unknown")

        data["log"].append(f"🧠 improver: detected issue in {layer}")

        # 👉 реакция на ошибки
        if layer == "execution":
            data["decision"] = "improve_module"
            data["log"].append("🛠 improver: fixing module")

        elif layer == "decision":
            data["decision"] = "simplify_decision"
            data["log"].append("🧠 improver: simplifying decision")

    # =========================
    # 📉 АНАЛИЗ ПРОГРЕССА
    # =========================

    score = data.get("evaluation", {}).get("score", 0)

    if score < 50:
        data["log"].append("📉 improver: low performance")

        # 👉 усиливаем развитие
        data["force_explore"] = True

    elif score > 85:
        data["log"].append("📈 improver: stable system")

    # =========================
    # 🧬 АНАЛИЗ ОПЫТА
    # =========================

    exp = data.get("experience", [])

    if len(exp) > 5:
        bad = [e for e in exp if e.get("score", 0) < 40]

        if len(bad) > 2:
            data["log"].append("🧹 improver: too many weak modules")
            data["decision"] = "improve_module"

    # =========================
    # 🔁 АНТИ-СТАГНАЦИЯ
    # =========================

    repeat = data.get("repeat_count", 0)

    if repeat >= 2:
        data["log"].append("🔁 improver: stagnation detected")
        data["force_explore"] = True

    return data
