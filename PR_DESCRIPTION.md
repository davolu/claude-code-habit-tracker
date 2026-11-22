Title: feat: add habit tracker web app with JSON store and API

## Summary

This PR adds a small Flask app for tracking daily habits and their streaks.

- Add a habit by name.
- List all habits.
- Mark a habit complete for today.
- Show the current streak for each habit.

It has a server-rendered HTML page (`templates/index.html`, `static/style.css`) and a small JSON API under `/api/habits`. Data is kept in a local `habits.json` file, which is gitignored.

## Notable decisions

- **UTC dates.** A "day" is an ISO date string (`YYYY-MM-DD`) in UTC, not a timestamp. "Today" is the UTC date, so a habit completed late in the local evening may count toward the next day.
- **Streak rule.** A streak is the number of consecutive completed days ending today or yesterday. If the last completion is before yesterday, the streak is 0.
- **Optional backfill date in the API.** `POST /api/habits/<id>/complete` accepts an optional `{"date": "YYYY-MM-DD"}`. With no body, it completes today. Past dates are allowed so a missed day can be filled in. Future dates return `400`. Malformed dates return `400`.
- **Atomic JSON writes.** `save_habits` writes to a temporary file in the same folder and then calls `os.replace`, so a reader never sees a half-written `habits.json`.
- **Store functions take an optional `path`.** Tests pass `tmp_path`, so they never touch the real `habits.json`.
- **No new dependencies beyond Flask.** Flask and pytest are pinned in `requirements.txt`.

## API

| Method | Path                        | Body (JSON)                       | Result                       |
| ------ | --------------------------- | --------------------------------- | ---------------------------- |
| GET    | `/api/habits`               | —                                 | List of habits               |
| POST   | `/api/habits`               | `{"name": "Read"}`                | `201` with the new habit     |
| POST   | `/api/habits/<id>/complete` | optional `{"date": "2026-11-21"}` | Habit; no date means today   |

Unknown habit ids return `404`. Bad input returns `400`.

## How to test

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q
```

Expected result: all tests pass (41 at the time of writing: 25 in `tests/test_habits.py` and 16 in `tests/test_api.py`).

To try the app by hand:

```bash
.venv/bin/python app.py
```

Then open http://127.0.0.1:5000. Running the app creates `habits.json` in the project folder on the first save.

## Review focus

- `habits.py`: the store, the atomic write, and `current_streak`.
- `app.py`: the input checks for the API, especially the `date` handling in `complete_habit_api`.
- Tests use `tmp_path`. Check that none of them write to the real `habits.json`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
