def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 8
    data.setdefault("log", []).append("module +8")
    return data
