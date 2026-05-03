import json
import os

MEM_FILE = "internet_memory_v2.json"


def load_memory():
    if not os.path.exists(MEM_FILE):
        return []

    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_memory(memory):
    try:
        with open(MEM_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except:
        pass


def update_weights(memory):
    """
    пересчитывает влияние паттернов
    """
    weights = {}

    for item in memory:
        patterns = item.get("patterns", [])
        score = item.get("score", 0)

        for p in patterns:
            if isinstance(p, str):
                weights[p] = weights.get(p, 0) + (score - 50) / 10

    return weights


def learn(data):
    """
    🔥 главный вход обучения
    """

    data.setdefault("log", [])

    evaluation = data.get("evaluation", {})
    score = evaluation.get("score", 50)

    decision = data.get("decision")
    module = data.get("module")

    if not decision:
        return data

    memory = load_memory()

    # =========================
    # 🧠 СОЗДАЁМ ОПЫТ
    # =========================
    patterns = []

    patterns.append(f"decision:{decision}")

    if module:
        patterns.append(f"module:{module}")

    if score >= 70:
        patterns.append("success_high")
    elif score >= 50:
        patterns.append("success_mid")
    else:
        patterns.append("fail_low")

    # =========================
    # 💾 ЗАПИСЬ В ПАМЯТЬ
    # =========================
    memory.append({
        "patterns": patterns,
        "score": score
    })

    # ограничение памяти (анти-рост)
    memory = memory[-2000:]

    save_memory(memory)

    # =========================
    # ⚙️ ОБНОВЛЕНИЕ ВЕСОВ
    # =========================
    weights = update_weights(memory)

    data["internet_weights"] = weights

    data["log"].append(
        f"🧠 LEARNED | score={score} | decision={decision} | module={module}"
    )

    return data
