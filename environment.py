import random


# =========================
# 🌍 INIT ENV (STABLE)
# =========================
def init_env(data):
    env = data.setdefault("env", {})

    env.setdefault("energy", 50)
    env.setdefault("knowledge", 0)
    env.setdefault("success", 0)
    env.setdefault("fail", 0)
    env.setdefault("experience", 0)
    env.setdefault("level", 1)
    env.setdefault("last_reward", 0)
    env.setdefault("history", [])
    env.setdefault("state", "stable")
    env.setdefault("entropy", 0)

    return env


# =========================
# ⚡ APPLY ACTION (SMART)
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

    # 🧬 создание нового (ВАЖНО)
    if "create module" in text or "module_" in text:
        reward += 8
        env["knowledge"] += 2

    # ♻️ повтор — плохо
    if "repeat" in text or "♻️" in text:
        reward -= 5
        env["entropy"] += 2

    # ⚙️ базовое действие
    if "базовое" in text:
        reward += 3

    # ❌ ошибка
    if "error" in text or "❌" in text:
        reward -= 10
        env["fail"] += 1

    return reward


# =========================
# 🌪 DYNAMIC WORLD (BALANCED)
# =========================
def world_dynamics(env):

    # хаос (контролируемый)
    entropy_change = random.randint(-2, 4)
    env["entropy"] += entropy_change

    # энергия утекает
    env["energy"] -= random.randint(1, 3)

    # защита от минуса
    env["energy"] = max(0, env["energy"])

    # если мало энергии → штраф
    if env["energy"] < 10:
        env["fail"] += 1
        env["entropy"] += 1

    # восстановление (ВАЖНО)
    if env["success"] > env["fail"]:
        env["energy"] += 2
        env["entropy"] -= random.randint(1, 3)

    # ограничения
    env["energy"] = min(env["energy"], 100)
    env["entropy"] = max(0, min(env["entropy"], 50))


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
# 🧬 LEVEL SYSTEM (SMART)
# =========================
def update_level(env):
    score = env["knowledge"] + env["experience"] + env["success"] * 2
    new_level = score // 50 + 1

    if new_level > env["level"]:
        env["level"] = new_level


# =========================
# 🎯 REWARD SYSTEM (ADVANCED)
# =========================
def calculate_reward(env, base_reward):

    reward = float(base_reward)

    # состояние
    if env["state"] == "growth":
        reward *= 1.5
    elif env["state"] == "decline":
        reward *= 0.7

    # уровень усиливает
    reward *= (1 + env["level"] * 0.1)

    # хаос штрафует
    reward -= env["entropy"] * 0.2

    # энергия влияет
    if env["energy"] < 10:
        reward *= 0.5

    # защита от мусора
    if reward < -50:
        reward = -50
    if reward > 100:
        reward = 100

    return int(reward)


# =========================
# 🧠 MAIN ENV FUNCTION
# =========================
def run_environment(data, action_log):

    env = init_env(data)

    # 1. влияние действия
    base_reward = apply_action(env, action_log)

    # 2. мир живёт
    world_dynamics(env)

    # 3. состояние
    update_state(env)

    # 4. уровень
    update_level(env)

    # 5. reward
    reward = calculate_reward(env, base_reward)

    # финализация
    env["last_reward"] = reward
    env["history"].append(reward)
    env["history"] = env["history"][-50:]

    return data, reward
