def run(context):
    """
    Evaluation v2

    Оценивает:

    - была ли задача
    - было ли выполнение
    - были ли ошибки
    - успешно ли выполнился модуль
    - есть ли результат
    """

    if not isinstance(context, dict):
        context = {}

    score = 50
    reasons = []

    task = context.get("task")
    status = context.get("status")
    result = context.get("result")
    execution_result = context.get("execution_result", {})
    errors = context.get("errors", [])
    log = context.get("log", [])

    # =====================================================
    # TASK
    # =====================================================

    if task:
        score += 10
    else:
        score -= 30
        reasons.append("no_task")

    # =====================================================
    # EXECUTION STATUS
    # =====================================================

    if status in ["ok", "success"]:
        score += 15

    elif status == "error":
        score -= 20
        reasons.append("execution_error")

    # =====================================================
    # EXECUTION RESULT
    # =====================================================

    if execution_result.get("success") is True:
        score += 15

    elif execution_result:
        score -= 10
        reasons.append("execution_failed")

    # =====================================================
    # RESULT
    # =====================================================

    if result:
        score += 10
    else:
        score -= 5
        reasons.append("no_result")

    # =====================================================
    # ERRORS
    # =====================================================

    if errors:

        penalty = min(len(errors) * 5, 30)

        score -= penalty

        reasons.append("errors_present")

    # =====================================================
    # LOG ANALYSIS
    # =====================================================

    useful = 0

    for line in log:

        text = str(line).lower()

        if any(
            x in text
            for x in [
                "decision",
                "success",
                "executed",
                "created module",
                "running"
            ]
        ):
            useful += 1

    score += min(useful, 10)

    # =====================================================
    # NORMALIZE
    # =====================================================

    score = max(0, min(100, score))

    if score >= 80:
        state = "excellent"

    elif score >= 60:
        state = "good"

    elif score >= 40:
        state = "neutral"

    else:
        state = "bad"

    evaluation = {
        "score": score,
        "result": state,
        "delta": score - 50,
        "reason": reasons
    }

    context["evaluation"] = evaluation

    return context