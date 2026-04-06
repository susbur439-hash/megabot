from flask import Flask, request, render_template_string
import sys
import os

# чтобы видел modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.analysis import analysis
from modules.decision import decision
from modules.action import action
from modules.execution import execution

app = Flask(__name__)

# 🔁 ядро
def run_task(task_text):
    data = {
        "task": task_text,
        "analysis": None,
        "decision": None,
        "result": None,
        "log": [],
        "memory": []
    }

    for i in range(3):
        data = analysis(data)
        data = decision(data)
        data = action(data)
        data = execution(data)

    return data


# 🎛 простая HTML панель
HTML = """
<!doctype html>
<title>Megabot Panel</title>
<h2>🧠 Megabot Control Panel</h2>
<form method=post>
  <input name=task style="width:300px" placeholder="Введите задачу">
  <input type=submit value=Запустить>
</form>

{% if result %}
<h3>Результат:</h3>
<pre>{{ result }}</pre>
{% endif %}
"""


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        task = request.form.get("task")
        result_data = run_task(task)
        result = str(result_data)

    return render_template_string(HTML, result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
