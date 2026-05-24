#!/usr/bin/env python3
"""
CLI for the Cursor demo task tracker.

Commands are implemented as subcommands (list, add, done, delete). Each handler
returns an integer exit code: 0 for success, 1 for user-facing errors (bad id,
invalid date). This follows Unix conventions so scripts can check $?.

Usage examples:
    python3 main.py list
    python3 main.py add "Buy milk" --due 2026-06-01
    python3 main.py done 3
"""

from __future__ import annotations

import argparse
import sys

from tasks import TaskStore

# ---------------------------------------------------------------------------
# Terminal styling (ANSI escape codes)
# Most modern terminals support these; no extra dependency required.
# ---------------------------------------------------------------------------
ANSI_RESET = "\033[0m"   # Clear all attributes after colored segment
ANSI_GREEN = "\033[32m"  # Completed tasks
ANSI_YELLOW = "\033[33m" # Pending tasks (checkbox bracket)
ANSI_BOLD = "\033[1m"    # Emphasize pending titles and ids
ANSI_DIM = "\033[2m"     # De-emphasize completed task text


def colored(text: str, color: str) -> str:
    """Wrap text in an ANSI color code and reset sequence."""
    return f"{color}{text}{ANSI_RESET}"


def cmd_list(store: TaskStore) -> int:
    """
    Print all tasks with color coding.

    Format per line:
        [x] id: title  (due: YYYY-MM-DD)
        [ ] id: title  (due: —)

    Done tasks use green/dim; pending use yellow/bold for the checkbox area.
    """
    tasks = store.list_all()
    if not tasks:
        print("No tasks yet. Try: python3 main.py add \"Your first task\"")
        return 0

    for task in tasks:
        # Checkbox column: "x" when done, space when still open.
        status = "x" if task.done else " "
        # Em dash when no due date so columns align visually in the terminal.
        due_label = task.due if task.due else "—"

        if task.done:
            # Muted styling — task is finished, less visual noise.
            line = (
                f"  [{colored(status, ANSI_GREEN)}] "
                f"{colored(str(task.id), ANSI_DIM)}: "
                f"{colored(task.title, ANSI_GREEN + ANSI_DIM)}  "
                f"(due: {colored(due_label, ANSI_DIM)})"
            )
        else:
            # Brighter styling draws attention to actionable items.
            line = (
                f"  [{colored(status, ANSI_YELLOW)}] "
                f"{colored(str(task.id), ANSI_BOLD)}: "
                f"{colored(task.title, ANSI_BOLD)}  "
                f"(due: {due_label})"
            )
        print(line)
    return 0


def cmd_add(store: TaskStore, title: str, due: str | None = None) -> int:
    """
    Add a new task and print confirmation.

    Delegates validation to TaskStore.add() / parse_due().
    """
    try:
        task = store.add(title, due=due)
    except ValueError as exc:
        # Invalid --due format; message already user-friendly from tasks.py.
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
    """
    Configure the CLI argument parser.

    Uses subparsers so each command has its own --help (e.g. main.py add --help).
    dest="command" is checked in main() to dispatch to the right handler.
    """
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
    """
    Entry point: parse args and dispatch to the appropriate command handler.

    Args:
        argv: Optional argument list (defaults to sys.argv[1:]). Useful for tests.

    Returns:
        Process exit code (0 = success, 1 = error or unknown command).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Single store instance per invocation; loads tasks.json on init.
    store = TaskStore()

    if args.command == "list":
        return cmd_list(store)
    if args.command == "add":
        return cmd_add(store, args.title, due=args.due)
    if args.command == "done":
        return cmd_done(store, args.id)
    if args.command == "delete":
        return cmd_delete(store, args.id)

    # Should not happen when subparsers are required, but keeps mypy/humans happy.
    parser.print_help()
    return 1


if __name__ == "__main__":
    # raise SystemExit passes our int return value to the shell as exit code.
    raise SystemExit(main())
