def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 7
    data.setdefault("log", []).append("module +7")
    return data
