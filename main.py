#!/usr/bin/env python3
"""CLI for the Cursor demo task tracker."""

from __future__ import annotations

import argparse
import sys

from tasks import TaskStore

# ANSI color codes
ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"

def colored(text: str, color: str) -> str:
    """Wrap text in an ANSI color code and reset sequence."""
    return f"{color}{text}{ANSI_RESET}"

def cmd_list(store: TaskStore) -> int:
    """Print all tasks with color coding: green/dim for done, yellow/bold for pending."""
    tasks = store.list_all()
    if not tasks:
        print("No tasks yet. Try: python3 main.py add \"Your first task\"")
        return 0
    for task in tasks:
        status = "x" if task.done else " "
        due_label = task.due if task.due else "—"
        if task.done:
            # Green and dim for completed
            line = f"  [{colored(status, ANSI_GREEN)}] {colored(str(task.id), ANSI_DIM)}: {colored(task.title, ANSI_GREEN+ANSI_DIM)}  (due: {colored(due_label, ANSI_DIM)})"
        else:
            # Yellow and bold for pending
            line = f"  [{colored(status, ANSI_YELLOW)}] {colored(str(task.id), ANSI_BOLD)}: {colored(task.title, ANSI_BOLD)}  (due: {due_label})"
        print(line)
    return 0


def cmd_add(store: TaskStore, title: str, due: str | None = None) -> int:
    """Add a new task and print confirmation; returns exit code 1 on validation error."""
    try:
        task = store.add(title, due=due)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    due_msg = f", due {task.due}" if task.due else ""
    print(f"Added task #{task.id}: {task.title}{due_msg}")
    return 0


def cmd_done(store: TaskStore, task_id: int) -> int:
    """Mark a task as complete by ID; returns exit code 1 if ID not found."""
    try:
        task = store.mark_done(task_id)
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Completed task #{task.id}: {task.title}")
    return 0


def cmd_delete(store: TaskStore, task_id: int) -> int:
    """Delete a task by ID; returns exit code 1 if ID not found."""
    try:
        task = store.delete(task_id)
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Deleted task #{task.id}: {task.title}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Configure and return the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        description="Cursor demo — simple task tracker",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="Show all tasks")

    add_p = sub.add_parser("add", help="Add a new task")
    add_p.add_argument("title", help="Task description")
    add_p.add_argument(
        "--due",
        metavar="YYYY-MM-DD",
        help="Optional due date (ISO format)",
    )

    done_p = sub.add_parser("done", help="Mark a task complete")
    done_p.add_argument("id", type=int, help="Task id")

    del_p = sub.add_parser("delete", help="Remove a task")
    del_p.add_argument("id", type=int, help="Task id")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args and dispatch to the appropriate command handler."""
    parser = build_parser()
    args = parser.parse_args(argv)
    store = TaskStore()

    if args.command == "list":
        return cmd_list(store)
    if args.command == "add":
        return cmd_add(store, args.title, due=args.due)
    if args.command == "done":
        return cmd_done(store, args.id)
    if args.command == "delete":
        return cmd_delete(store, args.id)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
