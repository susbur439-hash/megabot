import os
import json
from core_router import run

if __name__ == "__main__":

    task = os.environ.get("TASK_JSON", "развивай себя")

    try:
        parsed = json.loads(task)
        if isinstance(parsed, dict) and "task" in parsed:
            task = parsed["task"]
    except:
        pass

    print("🚀 MEGABOT START")
    print("🎯 TASK:", task)

    result = run(task)

    print("✅ RESULT:", result)
