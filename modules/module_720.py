def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 6
    data.setdefault("log", []).append("module +6")
    return data
