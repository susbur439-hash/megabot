from modules.decision import decide


def safe_import_execute():
    try:
        from modules.execution import execute
        return execute
    except Exception as e:
        print(f"[EXECUTION IMPORT ERROR] {e}")
        return None


def run_task(data):

    if not isinstance(data, dict):
        data = {"task": data}

    data.setdefault("log", [])

    print(f"[RUN] Выполнение задачи: {data}")

    # =========================
    # 🧠 DECISION LAYER
    # =========================
    data = decide(data)

    decision = data.get("decision")

    if not decision:
        data["status"] = "error"
        data["error"] = "No decision produced"
        return data

    data["log"].append(f"[RUN] decision -> {decision}")

    # =========================
    # ⚙ EXECUTION LAYER (SAFE)
    # =========================
    execute = safe_import_execute()

    if execute is None:
        data["status"] = "error"
        data["error"] = "execution module not available"
        data["log"].append("❌ execution missing")
        return data

    try:
        result = execute(data)

    except Exception as e:
        data["status"] = "error"
        data["error"] = str(e)
        data["log"].append(f"[RUN ERROR] {e}")
        return data

    # =========================
    # 🔗 MERGE RESULT
    # =========================
    if isinstance(result, dict):
        for k, v in result.items():
            if k == "log" and isinstance(v, list):
                data["log"].extend(v)
            else:
                data[k] = v

    data["status"] = data.get("status", "ok")

    return data
