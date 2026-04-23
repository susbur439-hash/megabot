def run(context):
    """
    Evaluation module:
    оценивает результат выполнения задачи и качество системы
    """

    score = 50
    reasons = []

    task = context.get("task", "")
    log = context.get("log", [])
    modules_created = context.get("modules_created", [])
    errors = context.get("errors", [])
    doctor_issues = context.get("doctor_issues", [])

    # =========================
    # 🧠 БАЗОВАЯ ОЦЕНКА
    # =========================
    if task:
        score += 10
    else:
        score -= 20
        reasons.append("no_task")

    # =========================
    # 🧱 МОДУЛИ
    # =========================
    if modules_created:
        score += len(modules_created) * 2
    else:
        score -= 5
        reasons.append("no_modules_created")

    # =========================
    # ❌ ОШИБКИ
    # =========================
    if errors:
        score -= len(errors) * 5
        reasons.append("errors_present")

    # =========================
    # ⚠️ СИСТЕМНЫЕ ПРОБЛЕМЫ
    # =========================
    if doctor_issues:
        score -= len(doctor_issues) * 3
        reasons.append("doctor_issues")

    # =========================
    # 📜 ЛОГ АНАЛИЗ
    # =========================
    if log:
        useful_logs = [l for l in log if "create_module" in l or "analysis" in l]
        score += len(useful_logs) * 1

    # =========================
    # 🔒 НОРМАЛИЗАЦИЯ
    # =========================
    if score > 100:
        score = 100
    if score < 0:
        score = 0

    # =========================
    # 📊 РЕЗУЛЬТАТ
    # =========================
    result = {
        "score": score,
        "result": "good" if score >= 70 else "neutral" if score >= 40 else "bad",
        "reason": reasons,
        "delta": score - 50
    }

    return result
