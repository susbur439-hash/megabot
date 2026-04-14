import os

def analyze(report):
    result = {
        "problems": []
    }

    files = report.get("files", [])
    empty = report.get("empty_files", [])

    # пустые файлы
    for f in empty:
        result["problems"].append(f"empty_file: {f}")

    # подозрительные setup
    for f in files:
        name = os.path.basename(f)
        if name.startswith("setup"):
            result["problems"].append(f"suspicious: {f}")

    # большие файлы
    for f in files:
        try:
            if os.path.getsize(f) > 5000:
                result["problems"].append(f"large_file: {f}")
        except:
            pass

    return result
