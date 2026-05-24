#!/usr/bin/env python3
"""CLI for the Cursor demo task tracker."""

from __future__ import annotations

import argparse
import sys

from tasks import TaskStore


def cmd_list(store: TaskStore) -> int:
    tasks = store.list_all()
    if not tasks:
        print("No tasks yet. Try: python3 main.py add \"Your first task\"")
        return 0
    for task in tasks:
        status = "x" if task.done else " "
        print(f"  [{status}] {task.id}: {task.title}")
    return 0


def cmd_add(store: TaskStore, title: str) -> int:
    task = store.add(title)
    print(f"Added task #{task.id}: {task.title}")
    return 0


def cmd_done(store: TaskStore, task_id: int) -> int:
    try:
        task = store.mark_done(task_id)
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Completed task #{task.id}: {task.title}")
    return 0


def cmd_delete(store: TaskStore, task_id: int) -> int:
    try:
        task = store.delete(task_id)
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Deleted task #{task.id}: {task.title}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cursor demo — simple task tracker",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="Show all tasks")

    add_p = sub.add_parser("add", help="Add a new task")
    add_p.add_argument("title", help="Task description")

    done_p = sub.add_parser("done", help="Mark a task complete")
    done_p.add_argument("id", type=int, help="Task id")

    del_p = sub.add_parser("delete", help="Remove a task")
    del_p.add_argument("id", type=int, help="Task id")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = TaskStore()

    if args.command == "list":
        return cmd_list(store)
    if args.command == "add":
        return cmd_add(store, args.title)
    if args.command == "done":
        return cmd_done(store, args.id)
    if args.command == "delete":
        return cmd_delete(store, args.id)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
