def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 15
    data.setdefault("log", []).append("module +15")
    return data
