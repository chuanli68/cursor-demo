# Cursor Demo — Task Tracker

A small sample project for learning how Cursor works: edit code, run commands, use Git, and connect to GitHub.

## What this project does

A command-line task tracker. You can add tasks, list them, mark them done, and delete them. Tasks are saved to `tasks.json` in this folder.

## Quick start

```bash
cd cursor-demo
python3 main.py --help
python3 main.py add "Learn Cursor"
python3 main.py list
python3 main.py done 1
```

## Run tests

```bash
python3 -m pytest test_tasks.py -v
```

## Project layout

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point (argparse) |
| `tasks.py` | Task storage and business logic |
| `test_tasks.py` | Unit tests |
| `tasks.json` | Created automatically when you add tasks |

## Try these in Cursor

These exercises show what the AI agent can help with. Open this folder in Cursor, then ask the chat (Agent mode) things like:

1. **Edit code** — *"Add a `priority` field (low/medium/high) to tasks"*
2. **Fix bugs** — *"The `list` command should sort incomplete tasks first"*
3. **Refactor** — *"Move JSON loading into a separate `storage.py` module"*
4. **Docs** — *"Add docstrings to all public functions in tasks.py"*
5. **Tests** — *"Add a test for deleting a task that doesn't exist"*

Use **@** in chat to reference files, e.g. `@tasks.py explain how save works`.

## Git workflow (local)

```bash
git status
git diff
git add .
git commit -m "Describe your change"
```

Cursor's Source Control panel (left sidebar) does the same: stage files, write a message, commit.

## Connect to GitHub

### 1. Log in to GitHub CLI (one-time)

In a terminal:

```bash
gh auth login
```

Follow the prompts (browser or token). Verify:

```bash
gh auth status
```

### 2. Create a remote repo and push

From the `cursor-demo` folder:

```bash
gh repo create cursor-demo --public --source=. --remote=origin --push
```

Or create the repo on github.com, then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/cursor-demo.git
git push -u origin main
```

### 3. Pull requests

After pushing a branch:

```bash
git checkout -b feature/my-change
# make changes, commit
git push -u origin feature/my-change
gh pr create --title "My change" --body "What and why"
```

Ask Cursor: *"Create a pull request for this branch"* — it can run `gh` for you if you're logged in.

## Cursor features cheat sheet

| Feature | How to use |
|---------|------------|
| **Agent** | Chat in Agent mode; it edits files and runs commands |
| **Inline edit** | Select code → Cmd+K → describe the change |
| **Tab completion** | Type code; accept AI suggestions with Tab |
| **Terminal** | View → Terminal; agent can run commands here |
| **Git** | Source Control icon; or ask agent to commit (when you ask) |
| **Rules** | `.cursor/rules` or project rules for consistent style |
| **@ mentions** | `@file`, `@folder`, `@docs` to focus context |

## License

MIT — sample code, use freely.
