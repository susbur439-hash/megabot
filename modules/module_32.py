def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 14
    data.setdefault("log", []).append("module +14")
    return data
