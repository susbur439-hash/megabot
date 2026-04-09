import os
import random
import json
import importlib.util


# =========================
# 💾 SAVE
# =========================
def save_to_memory(data):
    try:
        with open("memory.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)


# =========================
# 📁 REAL ACTIONS
# =========================
def create_file(filename):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("")
        return True, f"📁 file {filename} created"
    except Exception as e:
        return False, str(e)


def write_file(filename, content):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return True, f"✍️ written to {filename}"
    except Exception as e:
        return False, str(e)


def read_file(filename):
    try:
        if not os.path.exists(filename):
            return False, "file not found"
        with open(filename, "r", encoding="utf-8") as f:
            return True, f.read()
    except Exception as e:
        return False, str(e)


# =========================
# 🧠 TASK PARSER
# =========================
def parse_task_to_action(task):
    task = task.lower()

    if "создай файл" in task:
        return "create_file"
    if "запиши" in task:
        return "write_file"
    if "прочитай" in task:
        return "read_file"

    return None


# =========================
# 🚀 RUN MODULE
# =========================
def run_python_module(module_path, data):
    try:
        if not os.path.exists(module_path):
            data["log"].append("❌ module not found")
            return data, False

        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)

        if not spec or not spec.loader:
            data["log"].append("❌ load failed")
            return data, False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            result = module.run(data)

            if isinstance(result, dict):
                return result, True

        data["log"].append("⚠️ invalid module result")
        return data, False

    except Exception as e:
        data["log"].append(f"❌ module error: {e}")
        return data, False


# =========================
# 🧠 BEST MODULE
# =========================
def get_best_module(experience):
    if not experience:
        return None, 0

    best = max(experience, key=lambda x: x.get("score", 0))
    return best.get("module"), best.get("score", 0)


# =========================
# 📁 MODULES
# =========================
def get_all_modules():
    if not os.path.exists("modules"):
        return []
    return [f for f in os.listdir("modules") if f.endswith(".py")]


# =========================
# 🧬 CREATE MODULE
# =========================
def create_new_module(parent_exp=None):
    os.makedirs("modules", exist_ok=True)

    modules = get_all_modules()

    ids = []
    for m in modules:
        if m.startswith("module_"):
            try:
                ids.append(int(m.replace("module_", "").replace(".py", "")))
            except:
                pass

    new_id = max(ids, default=0) + 1
    name = f"module_{new_id}.py"
    path = os.path.join("modules", name)

    boost = random.randint(5, 15)

    code = f"""def run(data):
    boost = {boost}
    data.setdefault("goal", {{"progress": 0}})
    data.setdefault("log", [])

    data["goal"]["progress"] += boost
    data["log"].append("module {new_id} executed | +" + str(boost))

    return data
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return name.replace(".py", "")


# =========================
# 📊 SCORE
# =========================
def calculate_score(before, after, success=True):
    if not success:
        return 10

    delta = after - before

    if delta <= 0:
        return 20
    elif delta < 5:
        return 60
    elif delta < 15:
        return 80
    else:
        return 100


# =========================
# 🔥 EXECUTION (REAL)
# =========================
def execution(data):

    data.setdefault("log", [])
    data.setdefault("memory", [])
    data.setdefault("experience", [])
    data.setdefault("goal", {"progress": 0})

    task = data.get("task", "")
    decision = data.get("decision")

    before = data["goal"]["progress"]

    success = False
    module_used = None

    # =========================
    # 🧠 AUTO ACTION FROM TASK
    # =========================
    action = parse_task_to_action(task)

    if action == "create_file":
        success, msg = create_file("test.txt")
        data["log"].append(msg)

    elif action == "write_file":
        content = str(data.get("analysis", "нет анализа"))
        success, msg = write_file("test.txt", content)
        data["log"].append(msg)

    elif action == "read_file":
        success, content = read_file("test.txt")
        data["log"].append(f"📖 read: {content}")

    else:
        # fallback на старую систему
        best_module_name, _ = get_best_module(data["experience"])

        if decision == "run_module" and best_module_name:
            module_used = best_module_name
            path = os.path.join("modules", module_used + ".py")
            data, success = run_python_module(path, data)
        else:
            module_used = create_new_module()
            path = os.path.join("modules", module_used + ".py")
            data, success = run_python_module(path, data)

    # =========================
    # 📊 RESULT
    # =========================
    after = data["goal"]["progress"]
    delta = after - before

    data["last_delta"] = delta

    score = calculate_score(before, after, success)

    if module_used:
        exp = {
            "module": module_used,
            "score": score,
            "delta": delta,
            "time": len(data["memory"])
        }
        data["experience"].append(exp)

    data["memory"].append(decision)

    data["memory"] = data["memory"][-100:]
    data["log"] = data["log"][-200:]

    save_to_memory(data)

    return data
