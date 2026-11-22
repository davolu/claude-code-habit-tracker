"""Tests for the JSON API's input checks in app.py.

Every test writes to pytest's tmp_path, never to the real habits.json.
"""

from datetime import date
from pathlib import Path

import pytest

import app as web_app
import habits


@pytest.fixture(autouse=True)
def isolate_data_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the default data file at tmp_path so no test can touch the real one."""
    path = tmp_path / "habits.json"
    monkeypatch.setattr(habits, "DATA_FILE", path)
    return path


@pytest.fixture
def client():
    web_app.app.config["TESTING"] = True
    return web_app.app.test_client()


# --- POST /api/habits: body must be an object ------------------------------


@pytest.mark.parametrize("body", [["Read"], "Read", 5, True])
def test_add_habit_rejects_non_object_json(client, body) -> None:
    response = client.post("/api/habits", json=body)

    assert response.status_code == 400
    assert "JSON object" in response.get_json()["error"]


def test_add_habit_rejects_missing_body(client) -> None:
    response = client.post("/api/habits")

    assert response.status_code == 400


# --- POST /api/habits: name must be a non-empty string ---------------------


@pytest.mark.parametrize(
    "body",
    [
        {},  # name missing
        {"name": None},
        {"name": 123},
        {"name": ["Read"]},
        {"name": ""},
        {"name": "   "},
        {"name": "\t\n"},
    ],
)
def test_add_habit_rejects_bad_names(client, isolate_data_file: Path, body) -> None:
    response = client.post("/api/habits", json=body)

    assert response.status_code == 400
    assert "name" in response.get_json()["error"]
    assert not isolate_data_file.exists()


def test_add_habit_never_saves_a_habit_named_none(client) -> None:
    client.post("/api/habits", json={"name": None})

    assert habits.load_habits() == []


def test_add_habit_accepts_a_valid_name(client) -> None:
    response = client.post("/api/habits", json={"name": "  Read  "})

    assert response.status_code == 201
    assert response.get_json()["name"] == "Read"
    assert [h["name"] for h in habits.load_habits()] == ["Read"]


# --- POST /api/habits/<id>/complete: body must be an object if present -----


def test_complete_rejects_non_object_json(client) -> None:
    habit = habits.add_habit("Read")

    response = client.post(f"/api/habits/{habit['id']}/complete", json=["2026-11-21"])

    assert response.status_code == 400
    assert habits.load_habits()[0]["completions"] == []


def test_complete_without_body_marks_today(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(habits, "today", lambda: date(2026, 11, 22))
    habit = habits.add_habit("Read")

    response = client.post(f"/api/habits/{habit['id']}/complete")

    assert response.status_code == 200
    assert habits.load_habits()[0]["completions"] == ["2026-11-22"]
