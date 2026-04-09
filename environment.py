import random
import time


# =========================
# 🌍 INIT ENV
# =========================
def init_env(data):
    return data.setdefault("env", {
        "energy": 50,          # ресурс действий
        "knowledge": 0,        # накопленные знания
        "success": 0,          # успешные действия
        "fail": 0,             # ошибки
        "experience": 0,       # опыт
        "level": 1,            # уровень развития
        "last_reward": 0,
        "history": [],
        "state": "stable",     # stable / growth / decline
        "entropy": 0           # хаос среды
    })


# =========================
# ⚡ APPLY ACTION
# =========================
def apply_action(env, action_log):
    text = str(action_log).lower()

    reward = 0

    # 📁 реальные действия
    if "файл" in text or "file" in text:
        reward += 15
        env["knowledge"] += 5
        env["success"] += 1

    # 🚀 выполнение модулей
    if "module" in text:
        reward += 10
        env["experience"] += 3

    # ⚙️ базовое действие (слабое)
    if "базовое" in text:
        reward += 3

    # ❌ ошибка
    if "error" in text or "❌" in text:
        reward -= 10
        env["fail"] += 1

    return reward


# =========================
# 🌪 DYNAMIC WORLD
# =========================
def world_dynamics(env):
    # случайные изменения среды
    entropy_change = random.randint(-2, 5)
    env["entropy"] += entropy_change

    # энергия утекает всегда
    env["energy"] -= random.randint(1, 4)

    # если мало энергии — штраф
    if env["energy"] < 10:
        env["fail"] += 1

    # восстановление энергии
    if env["success"] > env["fail"]:
        env["energy"] += 2


# =========================
# 📊 STATE UPDATE
# =========================
def update_state(env):
    if env["success"] > env["fail"] * 2:
        env["state"] = "growth"
    elif env["fail"] > env["success"]:
        env["state"] = "decline"
    else:
        env["state"] = "stable"


# =========================
# 🧬 LEVEL SYSTEM
# =========================
def update_level(env):
    score = env["knowledge"] + env["experience"] + env["success"] * 2

    new_level = score // 50 + 1

    if new_level > env["level"]:
        env["level"] = new_level


# =========================
# 🎯 REWARD SYSTEM
# =========================
def calculate_reward(env, base_reward):
    reward = base_reward

    # бонус за рост
    if env["state"] == "growth":
        reward *= 1.5

    # штраф за деградацию
    if env["state"] == "decline":
        reward *= 0.7

    # уровень усиливает эффект
    reward *= (1 + env["level"] * 0.1)

    # штраф за хаос
    reward -= env["entropy"] * 0.2

    return int(reward)


# =========================
# 🧠 MAIN ENV FUNCTION
# =========================
def run_environment(data, action_log):

    env = init_env(data)

    # 1. действие влияет на мир
    base_reward = apply_action(env, action_log)

    # 2. мир живёт сам
    world_dynamics(env)

    # 3. обновление состояния
    update_state(env)

    # 4. уровень
    update_level(env)

    # 5. финальный reward
    reward = calculate_reward(env, base_reward)

    env["last_reward"] = reward
    env["history"].append(reward)
    env["history"] = env["history"][-50:]

    return data, reward
