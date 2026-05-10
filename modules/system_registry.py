# =========================================================
# 🧠 MEGABOT SYSTEM REGISTRY
# =========================================================

SYSTEM_REGISTRY = {}

# =========================================================
# 📦 REGISTER MODULE
# =========================================================

def register_module(name, module):

    if not name:
        return

    SYSTEM_REGISTRY[name] = module

    print(f"[Registry] registered: {name}")

# =========================================================
# 📦 GET MODULE
# =========================================================

def get_module(name):

    return SYSTEM_REGISTRY.get(name)

# =========================================================
# 📦 GET ALL
# =========================================================

def get_all_modules():

    return SYSTEM_REGISTRY

# =========================================================
# 📦 GET NAMES
# =========================================================

def get_module_names():

    return list(SYSTEM_REGISTRY.keys())

# =========================================================
# 📦 EXISTS
# =========================================================

def module_exists(name):

    return name in SYSTEM_REGISTRY

# =========================================================
# 📊 INFO
# =========================================================

def registry_info():

    return {
        "count": len(SYSTEM_REGISTRY),
        "modules": list(SYSTEM_REGISTRY.keys())
    }
