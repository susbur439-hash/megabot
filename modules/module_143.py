def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 10
    data.setdefault("log", []).append("module +10")
    return data
