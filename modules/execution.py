def execution(data):
    print("EXECUTION:", data["result"])

    # 💾 запись в лог (память)
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")

    data["log"].append("execution complete")
    return data
