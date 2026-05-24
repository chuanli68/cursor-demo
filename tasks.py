"""Task storage and operations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

DEFAULT_STORE = Path(__file__).parent / "tasks.json"


@dataclass
class Task:
    id: int
    title: str
    done: bool = False


class TaskStore:
    def __init__(self, path: Path = DEFAULT_STORE) -> None:
        self.path = path
        self._tasks: List[Task] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self._tasks = []
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self._tasks = [Task(**item) for item in data]

    def _save(self) -> None:
        payload = [asdict(t) for t in self._tasks]
        self.path.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

    def list_all(self) -> List[Task]:
        return list(self._tasks)

    def add(self, title: str) -> Task:
        next_id = max((t.id for t in self._tasks), default=0) + 1
        task = Task(id=next_id, title=title.strip())
        self._tasks.append(task)
        self._save()
        return task

    def mark_done(self, task_id: int) -> Task:
        task = self._get(task_id)
        task.done = True
        self._save()
        return task

    def delete(self, task_id: int) -> Task:
        task = self._get(task_id)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        self._save()
        return task

    def _get(self, task_id: int) -> Task:
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"No task with id {task_id}")
