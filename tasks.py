"""Task storage and operations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional

DEFAULT_STORE = Path(__file__).parent / "tasks.json"


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    due: Optional[str] = None  # ISO date YYYY-MM-DD


def parse_due(value: Optional[str]) -> Optional[str]:
    """Validate that a due date string is in YYYY-MM-DD format; return None if empty."""
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid due date '{text}'; use YYYY-MM-DD") from exc
    return text


class TaskStore:
    def __init__(self, path: Path = DEFAULT_STORE) -> None:
        self.path = path
        self._tasks: List[Task] = []
        self._load()

    def _load(self) -> None:
        """Read tasks from the JSON file into memory; starts empty if file doesn't exist."""
        if not self.path.exists():
            self._tasks = []
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self._tasks = [Task(**item) for item in data]

    def _save(self) -> None:
        """Serialize all in-memory tasks to the JSON file."""
        payload = [asdict(t) for t in self._tasks]
        self.path.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

    def list_all(self) -> List[Task]:
        """Return a copy of all tasks in insertion order."""
        return list(self._tasks)

    def add(self, title: str, due: Optional[str] = None) -> Task:
        """Create a new task with an auto-incremented ID and optional due date."""
        next_id = max((t.id for t in self._tasks), default=0) + 1
        task = Task(id=next_id, title=title.strip(), due=parse_due(due))
        self._tasks.append(task)
        self._save()
        return task

    def mark_done(self, task_id: int) -> Task:
        """Mark a task as complete and persist the change."""
        task = self._get(task_id)
        task.done = True
        self._save()
        return task

    def delete(self, task_id: int) -> Task:
        """Remove a task by ID and persist the change; returns the deleted task."""
        task = self._get(task_id)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        self._save()
        return task

    def _get(self, task_id: int) -> Task:
        """Look up a task by ID; raises KeyError if not found."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"No task with id {task_id}")
