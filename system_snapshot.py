import os
import json

OUTPUT_FILE = "full_system_snapshot.txt"
MAX_FILE_SIZE = 15000


def safe_read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if len(content) > MAX_FILE_SIZE:
                return content[:MAX_FILE_SIZE] + "\n... [TRUNCATED]"
            return content
    except:
        return "[BINARY OR ERROR]"


def scan():
    data = {
        "files": [],
        "python_files": [],
        "json_files": [],
        "empty_files": [],
        "large_files": []
    }

    for root, dirs, files in os.walk("."):
        for file in files:
            path = os.path.join(root, file)
            data["files"].append(path)

            if file.endswith(".py"):
                data["python_files"].append(path)

            if file.endswith(".json"):
                data["json_files"].append(path)

            try:
                size = os.path.getsize(path)
                if size == 0:
                    data["empty_files"].append(path)
                if size > 50000:
                    data["large_files"].append(path)
            except:
                pass

    return data


def main():
    report = []

    report.append("=== FILE STRUCTURE ===")
    scan_data = scan()

    for f in scan_data["files"]:
        report.append(f)

    report.append("\n=== PYTHON FILES ===")
    for f in scan_data["python_files"]:
        report.append(f)

    report.append("\n=== JSON FILES ===")
    for f in scan_data["json_files"]:
        report.append(f)

    report.append("\n=== EMPTY FILES ===")
    for f in scan_data["empty_files"]:
        report.append(f)

    report.append("\n=== LARGE FILES ===")
    for f in scan_data["large_files"]:
        report.append(f)

    report.append("\n=== FILE CONTENTS ===")

    for f in scan_data["python_files"] + scan_data["json_files"]:
        report.append(f"\n--- {f} ---\n")
        report.append(safe_read(f))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(report))

    print(f"✅ Full snapshot saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
