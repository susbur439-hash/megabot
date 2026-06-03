import json
import os


def run(context):

    print("[Learning] START")

    memory_file = "memory.json"
    scores_file = "module_scores.json"

    # =========================
    # MEMORY LOAD
    # =========================

    memory = {
        "experiences": [],
        "learning_log": []
    }

    if os.path.exists(memory_file):
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                memory.update(json.load(f))
        except:
            pass

    experiences = memory.get("experiences", [])
    learning_log = memory.get("learning_log", [])

    # =========================
    # MODULE SCORES LOAD
    # =========================

    module_scores = {}

    if os.path.exists(scores_file):
        try:
            with open(scores_file, "r", encoding="utf-8") as f:
                module_scores = json.load(f)
        except:
            pass

    # =========================
    # CONTEXT
    # =========================

    task = context.get("task", "unknown")

    evaluation = context.get("evaluation", {})
    score = evaluation.get("score", 50)

    module_name = (
        context.get("module")
        or context.get("last_module")
        or "unknown"
    )

    modules_created = context.get("modules_created", [])

    # =========================
    # EXPERIENCE
    # =========================

    experience = {
        "task": task,
        "score": score,
        "module": module_name,
        "success": score >= 70
    }

    experiences.append(experience)

    # =========================
    # TREND
    # =========================

    trend = "stable"

    last_scores = [e.get("score", 50) for e in experiences[-10:]]

    if len(last_scores) >= 3:

        if last_scores[-1] > last_scores[0]:
            trend = "improving"

        elif last_scores[-1] < last_scores[0]:
            trend = "declining"

    # =========================
    # MODULE STATISTICS
    # =========================

    stats = module_scores.get(module_name, {
        "runs": 0,
        "success": 0,
        "avg_score": 50,
        "disabled": False
    })

    stats["runs"] += 1

    if score >= 70:
        stats["success"] += 1

    old_avg = stats["avg_score"]

    stats["avg_score"] = round(
        ((old_avg * (stats["runs"] - 1)) + score)
        / stats["runs"],
        2
    )

    # auto-disable bad module

    if (
        stats["runs"] >= 5
        and stats["avg_score"] < 30
    ):
        stats["disabled"] = True

    module_scores[module_name] = stats

    # =========================
    # INSIGHTS
    # =========================

    insights = []

    if trend == "improving":
        insights.append("system performance improving")

    elif trend == "declining":
        insights.append("system performance declining")

    if score < 40:
        insights.append("low quality output detected")

    if len(modules_created) > 3:
        insights.append("too many modules created")

    if stats["disabled"]:
        insights.append(
            f"module {module_name} disabled"
        )

    # =========================
    # LEARNING LOG
    # =========================

    learning_log.append({
        "task": task,
        "module": module_name,
        "score": score,
        "trend": trend,
        "insights": insights
    })

    # =========================
    # SAVE MEMORY
    # =========================

    memory["experiences"] = experiences[-100:]
    memory["learning_log"] = learning_log[-100:]

    try:
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(
                memory,
                f,
                ensure_ascii=False,
                indent=2
            )
    except:
        pass

    # =========================
    # SAVE SCORES
    # =========================

    try:
        with open(scores_file, "w", encoding="utf-8") as f:
            json.dump(
                module_scores,
                f,
                ensure_ascii=False,
                indent=2
            )
    except:
        pass

    print("[Learning] DONE")

    return {
        "status": "ok",
        "trend": trend,
        "module": module_name,
        "module_stats": stats,
        "insights": insights,
        "total_experiences": len(experiences)
    }