import os

# защищённые зоны (нельзя трогать)
PROTECTED = [
    "main.py",
    "run.py",
    "megabot_core"
]

def is_protected(path):
    for p in PROTECTED:
        if p in path:
            return True
    return False


def analyze(report):
    result = {
        "problems": [],
        "actions": [],
        "summary": {
            "critical": 0,
            "warning": 0,
            "info": 0
        }
    }

    files = report.get("files", [])
    empty = report.get("empty_files", [])

    # --- ПУСТЫЕ ФАЙЛЫ ---
    for f in empty:
        level = "warning"

        result["problems"].append({
            "type": "empty_file",
            "path": f,
            "level": level
        })

        result["summary"][level] += 1

        if not is_protected(f):
            result["actions"].append({
                "type": "delete_file",
                "path": f
            })
        else:
            result["actions"].append({
                "type": "ignore",
                "path": f
            })

    # --- ПОДОЗРИТЕЛЬНЫЕ setup ---
    for f in files:
        name = os.path.basename(f)

        if name.startswith("setup"):
            level = "warning"

            result["problems"].append({
                "type": "suspicious_setup",
                "path": f,
                "level": level
            })

            result["summary"][level] += 1

            if not is_protected(f):
                result["actions"].append({
                    "type": "inspect_file",
                    "path": f
                })
            else:
                result["actions"].append({
                    "type": "ignore",
                    "path": f
                })

    # --- БОЛЬШИЕ ФАЙЛЫ ---
    for f in files:
        try:
            size = os.path.getsize(f)

            if size > 5000:
                level = "info"

                result["problems"].append({
                    "type": "large_file",
                    "path": f,
                    "size": size,
                    "level": level
                })

                result["summary"][level] += 1

                result["actions"].append({
                    "type": "refactor_candidate",
                    "path": f
                })

        except:
            pass

    return result
