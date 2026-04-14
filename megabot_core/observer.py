import os

def scan_project(root):
    report = {
        "files": [],
        "empty_files": [],
        "dirs": []
    }

    for path, dirs, files in os.walk(root):
        for d in dirs:
            report["dirs"].append(os.path.join(path, d))

        for f in files:
            full = os.path.join(path, f)
            report["files"].append(full)

            try:
                if os.path.getsize(full) == 0:
                    report["empty_files"].append(full)
            except:
                pass

    return report
