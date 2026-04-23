def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 5
    data.setdefault("log", []).append("module +5")
    return data
