def execution(data):

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    module_used = None
    success = False

    best_module, best_score = get_best_module(data["experience"])
    decision = data.get("decision")

    # =========================
    # 🧠 АНТИ-ЗАЦИКЛИВАНИЕ
    # =========================
    recent = data["memory"][-5:] if len(data["memory"]) >= 5 else data["memory"]

    too_many_improves = recent.count("improve_module") >= 3
    too_many_ideas = recent.count("generate_idea") >= 3

    before = data["goal"].get("progress", 0)

    # =========================
    # 🎯 ACTION MAPPING (УЛУЧШЕННЫЙ)
    # =========================
    if decision == "run_module" and best_module:
        action = "run"

    elif decision == "improve_module" and best_module:

        if best_score < 60:
            action = "create"
            data["log"].append("🔁 weak module → recreate")

        elif too_many_improves:
            action = "create"
            data["log"].append("🔁 anti-loop improve → create")

        else:
            action = "improve"

    elif decision == "generate_idea":

        if too_many_ideas:
            action = "create"
            data["log"].append("🔁 anti-loop idea → create")
        else:
            action = "idea"

    else:
        action = "create"

    # =========================
    # 💡 IDEA
    # =========================
    if action == "idea":
        boost, behavior = generate_idea_module()

        data["goal"]["progress"] += boost
        success = True
        module_used = "idea"

        data["log"].append(f"💡 idea | behavior={behavior} | boost={boost}")
        data["result"] = "idea generated"

    # =========================
    # CREATE
    # =========================
    elif action == "create":
        parent = {"module": best_module, "score": best_score} if best_module else None

        module_used = create_new_module(parent)
        path = os.path.join("modules", module_used + ".py")

        data, success = run_python_module(path, data)
        data["result"] = "module created"

    # =========================
    # RUN
    # =========================
    elif action == "run":
        path = os.path.join("modules", best_module + ".py")

        module_used = best_module
        data, success = run_python_module(path, data)
        data["result"] = "module executed"

    # =========================
    # IMPROVE
    # =========================
    elif action == "improve":
        if improve_existing_module(best_module):
            module_used = best_module
            data["goal"]["progress"] += 2
            success = True
            data["result"] = "module improved"
        else:
            data["result"] = "improve failed"

    after = data["goal"].get("progress", 0)

    delta = after - before
    data["last_delta"] = delta
    data["success"] = success

    # =========================
    # SCORE
    # =========================
    score = calculate_score(before, after, success)

    if module_used:
        data["experience"].append({
            "module": module_used,
            "score": score,
            "time": len(data["memory"])
        })

    # =========================
    # CLEANUP
    # =========================
    cleanup_modules(data)

    # =========================
    # MEMORY
    # =========================
    data["memory"].append(decision)
    data["memory"] = data["memory"][-100:]

    data["log"] = data["log"][-200:]

    # =========================
    # LOG
    # =========================
    data["log"].append(
        f"execution: {action} | module: {module_used} | success: {success} | delta: {delta} | score: {score}"
    )

    save_to_memory(data)

    return data
