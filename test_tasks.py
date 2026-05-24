"""
Tests for tasks.py.

Run with:
    python3 -m pytest test_tasks.py -v

Fixtures use pytest's tmp_path so each test gets an isolated tasks.json file
and never touches the developer's real task data.
"""

import json
from pathlib import Path

import pytest

from tasks import TaskStore


@pytest.fixture
def store_path(tmp_path: Path) -> Path:
    """Path to a fresh JSON file in a temporary directory."""
    return tmp_path / "tasks.json"


@pytest.fixture
def store(store_path: Path) -> TaskStore:
    """TaskStore wired to the temporary file from store_path."""
    return TaskStore(path=store_path)


def test_add_and_list(store: TaskStore) -> None:
    """Adding tasks assigns incrementing ids and preserves insertion order."""
    store.add("First")
    store.add("Second")
    tasks = store.list_all()
    assert len(tasks) == 2
    assert tasks[0].title == "First"
    assert tasks[1].title == "Second"
    assert tasks[1].id == 2


def test_mark_done(store: TaskStore) -> None:
    """mark_done flips the done flag and persists it."""
    task = store.add("Finish demo")
    store.mark_done(task.id)
    assert store.list_all()[0].done is True


def test_delete(store: TaskStore) -> None:
    """delete removes only the targeted id; other tasks remain."""
    t1 = store.add("Keep")
    store.add("Remove")
    store.delete(2)
    remaining = store.list_all()
    assert len(remaining) == 1
    assert remaining[0].id == t1.id


def test_mark_done_unknown_id(store: TaskStore) -> None:
    """Operations on missing ids raise KeyError with a clear message."""
    with pytest.raises(KeyError, match="No task with id 99"):
        store.mark_done(99)


def test_add_with_due_date(store: TaskStore) -> None:
    """Valid ISO due dates are stored on the task object."""
    task = store.add("Ship feature", due="2026-06-01")
    assert task.due == "2026-06-01"


def test_add_invalid_due_date(store: TaskStore) -> None:
    """Malformed due strings are rejected before writing to disk."""
    with pytest.raises(ValueError):
        store.add("Bad date", due="not-a-date")


def test_load_tasks_without_due_field(store_path: Path) -> None:
    """
    Backward compatibility: JSON saved before due dates were added.

    Tasks without a "due" key should load with due=None.
    """
    store_path.write_text(
        '[{"id": 1, "title": "Legacy", "done": false}]',
        encoding="utf-8",
    )
    store = TaskStore(path=store_path)
    assert store.list_all()[0].due is None


def test_persistence(store: TaskStore, store_path: Path) -> None:
    """Data written by one TaskStore instance is visible after reload."""
    store.add("Persist me")
    data = json.loads(store_path.read_text())
    assert data[0]["title"] == "Persist me"

    reloaded = TaskStore(path=store_path)
    assert reloaded.list_all()[0].title == "Persist me"


def test_due_date_persistence(store: TaskStore, store_path: Path) -> None:
    """Due dates round-trip through JSON save and reload."""
    store.add("With due", due="2026-12-31")
    data = json.loads(store_path.read_text())
    assert data[0]["due"] == "2026-12-31"

    reloaded = TaskStore(path=store_path)
    assert reloaded.list_all()[0].due == "2026-12-31"
