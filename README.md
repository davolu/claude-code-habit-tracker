# Habit Tracker

A small web app for tracking daily habits and streaks.

## Features

- Add a habit by name
- List all habits
- Mark a habit complete for today
- Show the current streak for each habit
- Data is stored in a local `habits.json` file (created on first save, not committed)

Days are UTC dates in `YYYY-MM-DD` form.

## Install

Requires Python 3.10 or newer.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python app.py
```

Then open http://127.0.0.1:5000 in a browser.

## API

| Method | Path                           | Body (JSON)            | Result                          |
| ------ | ------------------------------ | ---------------------- | ------------------------------- |
| GET    | `/api/habits`                  | —                      | List of habits                  |
| POST   | `/api/habits`                  | `{"name": "Read"}`     | `201` with the new habit        |
| POST   | `/api/habits/<id>/complete`    | optional `{"date": "2026-11-21"}` | Habit; no date means today |

- A habit looks like `{"id": 1, "name": "Read", "completed_today": false, "streak": 0}`.
- `date` must be `YYYY-MM-DD` and cannot be in the future (`400` otherwise). Past dates are allowed, so this is how you backfill a day.
- Unknown habit ids return `404`.
- Bad input returns `400`: a body that is not a JSON object, a `name` that is missing, not a string, or only whitespace, and a `date` that is malformed or in the future.

## Test

```bash
.venv/bin/pytest -q
```

pytest covers `habits.py` with 25 tests in `tests/test_habits.py`. `tests/test_api.py` covers the API's input checks. All tests write to temporary folders, never to the real `habits.json`.

## Claude Code

The project includes Claude Code customizations in `.claude/`:

- **`/ship`**: a project skill (`.claude/skills/ship/SKILL.md`). Type `/ship` to run the tests. If they pass, it shows `git status` and `git diff --stat` and drafts a commit message. It never commits or pushes on its own.
- **`test-writer` subagent**: `.claude/agents/test-writer.md`. Ask Claude to add tests and it writes focused pytest tests using `tmp_path`, never touching the real `habits.json`.
- **Hook**: `.claude/hooks/block-rm.sh`, registered in `.claude/settings.json` as a `PreToolUse` hook on Bash. It blocks `rm -rf` commands and any `rm` that targets `habits.json`.
- **Permissions**: `.claude/settings.json` allows reading files and running `.venv/bin/pytest`, and denies `rm -rf`.

MCP servers are not configured yet. To add one later, run `claude mcp add --transport http <name> <url>`.
