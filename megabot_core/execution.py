import os
import json
import time


def log_call(module, action_type, path=None):
    try:
        with open("runtime_log.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {"calls": []}

    data["calls"].append({
        "module": module,
        "type": action_type,
        "path": path,
        "timestamp": time.time()
    })

    with open("runtime_log.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def execute(actions):
    result = []

    for act in actions:
        t = act.get("type")
        path = act.get("path")
        module = act.get("module", "execution_core")

        try:
            # 🔥 DELETE
            if t == "delete_file":
                if os.path.exists(path):
                    os.remove(path)
                    result.append(f"deleted: {path}")

                log_call(module, "delete_file", path)

            # 📖 READ
            elif t == "read_file":
                content = None

                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                result.append({path: (content[:200] if content else None)})

                log_call(module, "read_file", path)

            # 🧠 UNKNOWN ACTION
            else:
                log_call(module, "unknown", path)
                result.append(f"unknown action: {t}")

        except Exception as e:
            log_call(module, "error", path)
            result.append(f"error: {path} -> {e}")

    return result
