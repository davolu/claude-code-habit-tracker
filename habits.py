"""Data store and streak logic for habits.

Habits are saved in habits.json next to this file. Each habit looks like:
    {"id": 1, "name": "Read", "completions": ["2026-11-20", "2026-11-21"]}
Dates are ISO strings (YYYY-MM-DD) in UTC.
"""

import json
import os
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "habits.json"


def today() -> date:
    """Return today's date in UTC."""
    return datetime.now(timezone.utc).date()


def _data_file(path: Path | None) -> Path:
    """Use the given path, or the default habits.json when none is given."""
    return DATA_FILE if path is None else path


def load_habits(path: Path | None = None) -> list[dict]:
    """Return all habits. Returns an empty list if the file does not exist yet."""
    data_file = _data_file(path)
    if not data_file.exists():
        return []
    with data_file.open() as f:
        return json.load(f)


def save_habits(habits: list[dict], path: Path | None = None) -> None:
    """Write all habits to the JSON file.

    Writes to a temporary file in the same folder, then swaps it into place,
    so a reader never sees a half-written file.
    """
    data_file = _data_file(path)
    fd, tmp_name = tempfile.mkstemp(dir=data_file.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(habits, f, indent=2)
        os.replace(tmp_name, data_file)
    finally:
        # After a successful replace this file no longer exists, so this is a no-op.
        Path(tmp_name).unlink(missing_ok=True)


def add_habit(name: str, path: Path | None = None) -> dict:
    """Add a new habit with a new id and return it. Duplicate names are allowed.

    Raises ValueError if the name is empty or only whitespace.
    """
    if not name.strip():
        raise ValueError("habit name must not be empty")
    habits = load_habits(path)
    next_id = max((h["id"] for h in habits), default=0) + 1
    habit = {"id": next_id, "name": name, "completions": []}
    habits.append(habit)
    save_habits(habits, path)
    return habit


def mark_complete(habit_id: int, day: date | None = None, path: Path | None = None) -> dict | None:
    """Mark a habit as done on the given day (default: today, UTC).

    Completing the same day twice does nothing. Returns None if the habit does not exist.
    """
    if day is None:
        day = today()
    habits = load_habits(path)
    for habit in habits:
        if habit["id"] == habit_id:
            day_text = day.isoformat()
            if day_text not in habit["completions"]:
                habit["completions"].append(day_text)
                habit["completions"].sort()
            save_habits(habits, path)
            return habit
    return None


def current_streak(completions: list[str], now: date) -> int:
    """Count consecutive completed days, ending today or yesterday.

    If the last completion is before yesterday, the streak is 0.
    """
    done = {date.fromisoformat(d) for d in completions}
    if now in done:
        day = now
    elif now - timedelta(days=1) in done:
        day = now - timedelta(days=1)
    else:
        return 0

    streak = 0
    while day in done:
        streak += 1
        day -= timedelta(days=1)
    return streak


def summarize(habit: dict, now: date) -> dict:
    """Return the habit fields the web page and API show."""
    return {
        "id": habit["id"],
        "name": habit["name"],
        "completed_today": now.isoformat() in habit["completions"],
        "streak": current_streak(habit["completions"], now),
    }
