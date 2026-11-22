"""Tests for the habit data store and streak logic in habits.py.

Every test writes to pytest's tmp_path, never to the real habits.json.
"""

from datetime import date
from pathlib import Path

import pytest

import habits

NOW = date(2026, 11, 22)


@pytest.fixture(autouse=True)
def isolate_data_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the default data file at tmp_path so no test can touch the real one."""
    path = tmp_path / "default-habits.json"
    monkeypatch.setattr(habits, "DATA_FILE", path)
    return path


@pytest.fixture
def store(tmp_path: Path) -> Path:
    """A path for a habits file that does not exist yet."""
    return tmp_path / "habits.json"


# --- add_habit -------------------------------------------------------------


def test_add_habit_stores_the_name(store: Path) -> None:
    habits.add_habit("Read", path=store)

    saved = habits.load_habits(path=store)
    assert len(saved) == 1
    assert saved[0]["name"] == "Read"
    assert saved[0]["completions"] == []


def test_add_habit_returns_the_new_habit(store: Path) -> None:
    habit = habits.add_habit("Read", path=store)

    assert habit["name"] == "Read"
    assert habit["completions"] == []
    assert isinstance(habit["id"], int)


def test_add_habit_ids_increment(store: Path) -> None:
    first = habits.add_habit("Read", path=store)
    second = habits.add_habit("Run", path=store)
    third = habits.add_habit("Stretch", path=store)

    assert second["id"] == first["id"] + 1
    assert third["id"] == second["id"] + 1


def test_add_habit_allows_duplicate_names(store: Path) -> None:
    first = habits.add_habit("Read", path=store)
    second = habits.add_habit("Read", path=store)

    assert first["id"] != second["id"]
    assert len(habits.load_habits(path=store)) == 2


@pytest.mark.parametrize("name", ["", "   ", "\t", "\n  \t"])
def test_add_habit_rejects_empty_or_whitespace_names(store: Path, name: str) -> None:
    with pytest.raises(ValueError):
        habits.add_habit(name, path=store)

    assert habits.load_habits(path=store) == []


# --- load_habits -----------------------------------------------------------


def test_load_habits_empty_store_returns_empty_list(store: Path) -> None:
    assert not store.exists()
    assert habits.load_habits(path=store) == []


def test_load_habits_lists_all_habits_in_order(store: Path) -> None:
    habits.add_habit("Read", path=store)
    habits.add_habit("Run", path=store)

    names = [h["name"] for h in habits.load_habits(path=store)]
    assert names == ["Read", "Run"]


# --- mark_complete ---------------------------------------------------------


def test_mark_complete_explicit_day(store: Path) -> None:
    habit = habits.add_habit("Read", path=store)

    updated = habits.mark_complete(habit["id"], date(2026, 11, 20), path=store)

    assert updated is not None
    assert updated["completions"] == ["2026-11-20"]
    assert habits.load_habits(path=store)[0]["completions"] == ["2026-11-20"]


def test_mark_complete_defaults_to_today(store: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(habits, "today", lambda: NOW)
    habit = habits.add_habit("Read", path=store)

    updated = habits.mark_complete(habit["id"], path=store)

    assert updated is not None
    assert updated["completions"] == ["2026-11-22"]


def test_mark_complete_twice_same_day_is_a_no_op(store: Path) -> None:
    habit = habits.add_habit("Read", path=store)

    habits.mark_complete(habit["id"], NOW, path=store)
    updated = habits.mark_complete(habit["id"], NOW, path=store)

    assert updated is not None
    assert updated["completions"] == ["2026-11-22"]
    assert habits.load_habits(path=store)[0]["completions"] == ["2026-11-22"]


def test_mark_complete_keeps_completions_sorted(store: Path) -> None:
    habit = habits.add_habit("Read", path=store)

    habits.mark_complete(habit["id"], date(2026, 11, 22), path=store)
    habits.mark_complete(habit["id"], date(2026, 11, 20), path=store)
    updated = habits.mark_complete(habit["id"], date(2026, 11, 21), path=store)

    assert updated is not None
    assert updated["completions"] == ["2026-11-20", "2026-11-21", "2026-11-22"]


def test_mark_complete_unknown_id_returns_none_and_changes_nothing(store: Path) -> None:
    habits.add_habit("Read", path=store)
    before = habits.load_habits(path=store)

    result = habits.mark_complete(999, NOW, path=store)

    assert result is None
    assert habits.load_habits(path=store) == before


# --- current_streak --------------------------------------------------------


def test_streak_no_completions_is_zero() -> None:
    assert habits.current_streak([], NOW) == 0


def test_streak_only_today_is_one() -> None:
    assert habits.current_streak(["2026-11-22"], NOW) == 1


def test_streak_yesterday_still_counts() -> None:
    assert habits.current_streak(["2026-11-21"], NOW) == 1


def test_streak_last_completion_day_before_yesterday_is_zero() -> None:
    assert habits.current_streak(["2026-11-20"], NOW) == 0


def test_streak_consecutive_run_ending_today_counts_every_day() -> None:
    completions = ["2026-11-20", "2026-11-21", "2026-11-22"]
    assert habits.current_streak(completions, NOW) == 3


def test_streak_consecutive_run_ending_yesterday_counts_every_day() -> None:
    completions = ["2026-11-19", "2026-11-20", "2026-11-21"]
    assert habits.current_streak(completions, NOW) == 3


def test_streak_gap_resets_the_count() -> None:
    # 19 and 20 are a run, but 20 is missing before 21 and 22: only 21-22 count.
    completions = ["2026-11-18", "2026-11-19", "2026-11-21", "2026-11-22"]
    assert habits.current_streak(completions, NOW) == 2


def test_streak_old_run_with_gap_before_today_is_zero() -> None:
    completions = ["2026-11-15", "2026-11-16", "2026-11-17"]
    assert habits.current_streak(completions, NOW) == 0


def test_streak_future_date_is_ignored() -> None:
    assert habits.current_streak(["2026-11-23"], NOW) == 0


def test_streak_future_date_does_not_extend_the_run() -> None:
    completions = ["2026-11-21", "2026-11-22", "2026-11-23"]
    assert habits.current_streak(completions, NOW) == 2
