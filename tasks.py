"""
Task storage and operations.

This module is the data layer for the demo app. It defines the Task model,
validates due dates, and persists tasks to a JSON file via TaskStore.

Design notes:
  - Tasks live in memory (_tasks) and are written to disk on every mutation.
  - IDs are integers assigned sequentially (max existing id + 1).
  - Due dates are stored as ISO strings (YYYY-MM-DD) for simple JSON serialization.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional

# Default location for tasks.json — same directory as this source file.
DEFAULT_STORE = Path(__file__).parent / "tasks.json"


@dataclass
class Task:
    """
    A single todo item.

    Attributes:
        id: Unique identifier, never reused after delete.
        title: Human-readable description (whitespace trimmed on add).
        done: True once marked complete via mark_done().
        due: Optional ISO date string (YYYY-MM-DD), or None if unset.
    """

    id: int
    title: str
    done: bool = False
    due: Optional[str] = None  # ISO date YYYY-MM-DD


def parse_due(value: Optional[str]) -> Optional[str]:
    """
    Validate and normalize a due date string.

    Accepts None or blank input as "no due date". Otherwise requires a string
    that Python's date.fromisoformat() can parse (YYYY-MM-DD).

    Raises:
        ValueError: If the string is non-empty but not a valid ISO date.
    """
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        # fromisoformat enforces YYYY-MM-DD for date-only strings.
        date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid due date '{text}'; use YYYY-MM-DD") from exc
    return text


class TaskStore:
    """
    In-memory task collection backed by a JSON file.

    On construction, loads existing tasks from disk (if the file exists).
    Every public mutation (add, mark_done, delete) calls _save() so the file
    always reflects the latest state.
    """

    def __init__(self, path: Path = DEFAULT_STORE) -> None:
        """Initialize store and load tasks from path (creates empty list if missing)."""
        self.path = path
        self._tasks: List[Task] = []
        self._load()

    def _load(self) -> None:
        """
        Read tasks from the JSON file into memory.

        Expected file format: a JSON array of objects, each matching Task fields.
        Missing file → empty task list (first run).
        Older files without a "due" field still work because Task.due defaults to None.
        """
        if not self.path.exists():
            self._tasks = []
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        # Unpack each dict into a Task instance (extra keys would raise TypeError).
        self._tasks = [Task(**item) for item in data]

    def _save(self) -> None:
        """
        Serialize all in-memory tasks to the JSON file.

        Uses dataclasses.asdict() so field names match the on-disk schema.
        Pretty-prints with indent=2 for human-readable diffs in git/editor.
        """
        payload = [asdict(t) for t in self._tasks]
        self.path.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

    def list_all(self) -> List[Task]:
        """Return a shallow copy so callers cannot mutate internal list directly."""
        return list(self._tasks)

    def add(self, title: str, due: Optional[str] = None) -> Task:
        """
        Create a new task with an auto-incremented ID and optional due date.

        ID assignment: max of all existing ids + 1, or 1 if the list is empty.
        This means deleted IDs are not recycled (simpler for CLI users).
        """
        next_id = max((t.id for t in self._tasks), default=0) + 1
        task = Task(id=next_id, title=title.strip(), due=parse_due(due))
        self._tasks.append(task)
        self._save()
        return task

    def mark_done(self, task_id: int) -> Task:
        """Set done=True for the given id and write to disk."""
        task = self._get(task_id)
        task.done = True
        self._save()
        return task

    def delete(self, task_id: int) -> Task:
        """
        Remove a task by ID and persist.

        Returns the deleted Task so the CLI can confirm what was removed.
        """
        task = self._get(task_id)
        # Rebuild list excluding the target id (stable order for remaining items).
        self._tasks = [t for t in self._tasks if t.id != task_id]
        self._save()
        return task

    def _get(self, task_id: int) -> Task:
        """
        Look up a task by ID.

        Linear scan is fine for a demo; a dict keyed by id would scale better.
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"No task with id {task_id}")
