import os

def execute(actions):
    result = []

    for act in actions:
        t = act.get("type")
        path = act.get("path")

        try:
            if t == "delete_file":
                if os.path.exists(path):
                    os.remove(path)
                    result.append(f"deleted: {path}")

            elif t == "read_file":
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    result.append({path: content[:200]})

        except Exception as e:
            result.append(f"error: {path} -> {e}")

    return result
