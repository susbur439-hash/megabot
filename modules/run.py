from modules.decision import decide


def safe_import_execute():
    try:
        from modules.execution import execute
        return execute
    except Exception as e:
        print(f"[EXECUTION IMPORT ERROR] {e}")
        return None


# =========================
# 🛡️ DATA TYPE GUARD
# =========================
def normalize_data(data):
    if not isinstance(data, dict):
        data = {"task": str(data)}

    if not isinstance(data.get("log"), list):
        data["log"] = []

    if not isinstance(data.get("experience"), list):
        data["experience"] = []

    if not isinstance(data.get("evaluation"), dict):
        data["evaluation"] = {}

    return data


# =========================
# 🚀 RUN TASK
# =========================
def run_task(data):

    data = normalize_data(data)

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
    # 🧩 SAFE MERGE (CRITICAL FIX)
    # =========================
    if isinstance(result, dict):
        for k, v in result.items():

            # log merge
            if k == "log" and isinstance(v, list):
                data["log"].extend(v)

            # strict type safety (fix crash source)
            elif k == "experience":
                if isinstance(v, list):
                    data["experience"] = v

            elif k == "evaluation":
                if isinstance(v, dict):
                    data["evaluation"] = v

            elif k == "module":
                data["module"] = v

            elif k == "status":
                data["status"] = v

            else:
                data[k] = v

    # =========================
    # 🛡️ FINAL SAFETY CHECK
    # =========================
    data = normalize_data(data)

    data["status"] = data.get("status", "ok")

    return data
