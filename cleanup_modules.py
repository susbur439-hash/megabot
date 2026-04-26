import os
import re

path = "modules"

deleted = []
kept = []

pattern = re.compile(r"module_\d+\.py$")

for file in os.listdir(path):
    full = os.path.join(path, file)

    if not file.endswith(".py"):
        continue

    if pattern.match(file):
        os.remove(full)
        deleted.append(file)
    else:
        kept.append(file)

print("🧹 deleted:", len(deleted))
print("📦 kept:", kept)
