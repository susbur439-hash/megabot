import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from director import run

if __name__ == "__main__":
    task = "развивай себя"

    if len(sys.argv) > 1:
        task = sys.argv[1]

    run(task)
