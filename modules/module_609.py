def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 12
    data.setdefault("log", []).append("module +12")
    return data
