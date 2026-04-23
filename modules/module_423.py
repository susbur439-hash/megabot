def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 9
    data.setdefault("log", []).append("module +9")
    return data
