"""Flask web app: an HTML page plus a small JSON API for habits."""

from datetime import date

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

import habits

app = Flask(__name__)


@app.get("/")
def index():
    now = habits.today()
    rows = [habits.summarize(h, now) for h in habits.load_habits()]
    return render_template("index.html", habits=rows)


@app.post("/habits")
def add_habit_form():
    name = request.form.get("name", "").strip()
    if name:
        habits.add_habit(name)
    return redirect(url_for("index"))


@app.post("/habits/<int:habit_id>/complete")
def complete_habit_form(habit_id: int):
    if habits.mark_complete(habit_id, habits.today()) is None:
        abort(404)
    return redirect(url_for("index"))


@app.get("/api/habits")
def list_habits_api():
    now = habits.today()
    return jsonify([habits.summarize(h, now) for h in habits.load_habits()])


@app.post("/api/habits")
def add_habit_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="body must be a JSON object"), 400
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify(error="name must be a non-empty string"), 400
    habit = habits.add_habit(name.strip())
    return jsonify(habits.summarize(habit, habits.today())), 201


@app.post("/api/habits/<int:habit_id>/complete")
def complete_habit_api(habit_id: int):
    data = request.get_json(silent=True)
    if data is None:
        data = {}  # no body means "today"
    if not isinstance(data, dict):
        return jsonify(error="body must be a JSON object"), 400
    now = habits.today()

    day = now
    if data.get("date") is not None:
        try:
            day = date.fromisoformat(str(data["date"]))
        except ValueError:
            return jsonify(error="date must be YYYY-MM-DD"), 400
        if day.isoformat() != str(data["date"]):
            return jsonify(error="date must be YYYY-MM-DD"), 400
        if day > now:
            return jsonify(error="date cannot be in the future"), 400

    habit = habits.mark_complete(habit_id, day)
    if habit is None:
        return jsonify(error="habit not found"), 404
    return jsonify(habits.summarize(habit, now))


if __name__ == "__main__":
    app.run(debug=True)
