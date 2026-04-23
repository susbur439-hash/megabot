def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 11
    data.setdefault("log", []).append("module +11")
    return data
