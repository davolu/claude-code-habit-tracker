# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This is a course project at an early stage. The app and its store tests exist.

Files present:
- `app.py`: Flask entry point. HTML routes (`/`, `POST /habits`, `POST /habits/<id>/complete`) and JSON API (`/api/habits`, `POST /api/habits`, `POST /api/habits/<id>/complete`).
- `habits.py`: data store (`habits.json`) and streak logic. Uses UTC dates.
- `tests/test_habits.py`: pytest tests for `habits.py`. They use `tmp_path` and never touch the real `habits.json`.
- `pytest.ini`: sets `pythonpath = .` so tests can `import habits`, and `testpaths = tests`.
- `templates/index.html` and `static/style.css`: the HTML page.
- `requirements.txt`: pinned `Flask==3.1.3` and `pytest==9.2.0`.
- `README.md`, `.gitignore`, `CLAUDE.md`.

Store API (`habits.py`): `load_habits(path=None)`, `save_habits(habits, path=None)`, `add_habit(name, path=None)` (raises `ValueError` on empty or whitespace-only names), `mark_complete(habit_id, day=None, path=None)` (day defaults to today, UTC; returns `None` for an unknown id). `path=None` means the default `habits.json`. `current_streak(completions, now)` is pure. Tests pass `path=` explicitly.

## Planned design (from README.md)

- A small web app for tracking daily habits and streaks.
- Features: add a habit by name, list habits, mark a habit complete for today, show the current streak per habit.
- Persistence: a local JSON file. `.gitignore` excludes `habits.json`, so this is runtime data and should not be committed.
- Interface: a simple HTML page plus a small HTTP API.
- Tests: pytest.

## Stack

- Python 3.
- Flask, with a single `app.py` entry point.
- `habits.py` holds the data store and streak logic.
- Data lives in a local `habits.json` file. It is gitignored runtime data; never commit it.
- A server-rendered HTML page in `templates/index.html`, plus a small CSS file in `static/style.css`.
- pytest for tests, with tests in `tests/`.
- Virtualenv at `.venv`; dependencies pinned in `requirements.txt` at the repo root.

## Coding standards

- Plain, readable Python. Prefer simple functions over classes unless a class is clearly better.
- Type hints on public functions.
- Dates are ISO strings, `YYYY-MM-DD`, in UTC date terms. A "day" is an ISO date string, not a timestamp.
- A streak is the number of consecutive days a habit was completed, ending today or yesterday. If the last completion was before yesterday, the streak is 0.
- Never invent features that were not asked for.
- Do not print secrets or commit `.env` files (`.env`, `.env.*` are gitignored).
- After changing behaviour, run pytest and fix failures before finishing.
- Keep the HTML simple and readable. No JavaScript framework.

## Commands

- Create the venv and install: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Run the app: `.venv/bin/python app.py`
- Run tests: `.venv/bin/pytest -q` (25 tests in `tests/test_habits.py`)

## Conventions implied by `.gitignore`

- Python project (`.venv/`, `__pycache__/`, `.pytest_cache/`, `*.egg-info/`), so use a virtualenv named `.venv`.
- Secrets go in `.env` / `.env.*`, which are gitignored.
- Local-only Claude config (`.claude/settings.local.json`, `CLAUDE.local.md`) is gitignored and should stay out of commits.
