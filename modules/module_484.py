def run(data):
    data.setdefault("goal", {"progress": 0})
    data["goal"]["progress"] += 13
    data.setdefault("log", []).append("module +13")
    return data
