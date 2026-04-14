import os

def analyze(report):
    result = {
        "problems": [],
        "actions": []
    }

    files = report.get("files", [])
    empty = report.get("empty_files", [])

    for f in empty:
        result["problems"].append(f"empty_file: {f}")
        result["actions"].append({
            "type": "delete_file",
            "path": f
        })

    for f in files:
        name = os.path.basename(f)
        if name.startswith("setup"):
            result["problems"].append(f"suspicious: {f}")
            result["actions"].append({
                "type": "delete_file",
                "path": f
            })

    for f in files:
        try:
            if os.path.getsize(f) > 5000:
                result["problems"].append(f"large_file: {f}")
        except:
            pass

    return result
