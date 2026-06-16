# AGENTS.md

## Project Status

This repository is a clean rebuild.

The current formal project name is:

**Minimal Space for Simulated Listening**

“Groove Ear” is a historical codename and may appear in legacy materials.

The current project source of truth is:

1. `README.md`
2. files in this new repository
3. legacy materials only when explicitly referenced through `references/legacy_index.md`

If any legacy material conflicts with `README.md`, `README.md` wins.

---

## Required Working Workflow

For every task, follow this order:

1. Read `AGENTS.md`.
2. Read `README.md` to understand the current project baseline.
3. Read `references/legacy_index.md` before consulting any legacy material.
4. If legacy reference is needed, inspect the legacy project at:

   `D:\groove-ear`

5. Treat `D:\groove-ear` as read-only background material.
6. Extract only the useful essence from legacy materials.
7. Rewrite, simplify, or adapt legacy ideas into the new project.
8. Do not directly revive old project structure, old architecture, or old output sprawl.
9. If any legacy material is reused, update `docs/migration_log.md`.
10. Summarize what was changed, what legacy material was consulted, and what was intentionally not imported.

---

## Legacy Project Rules

The legacy project is located at:

`D:\groove-ear`

It is a reference archive only.

Codex may read files under this path for:
- historical concepts
- terminology
- earlier experiments
- old modeling attempts
- useful background context

Codex must not:
- modify anything under `D:\groove-ear`
- delete anything under `D:\groove-ear`
- rename anything under `D:\groove-ear`
- reformat anything under `D:\groove-ear`
- write new files under `D:\groove-ear`
- treat `D:\groove-ear` as the current project root
- continue the old architecture by default
- restore old V1/V2/V3 structures
- copy large legacy files directly into the new project
- import old debug outputs or unnecessary artifacts

Legacy material is allowed to influence the new project only after being intentionally selected, rewritten, and recorded.

---

## Migration Rule

Whenever legacy material is reused, update:

`docs/migration_log.md`

Each migration entry must include:

- legacy source path
- what was reused
- whether it was copied, rewritten, summarized, or only conceptually referenced
- why it belongs in the new project
- which current file received the migrated material

If no legacy material was used, do not update the migration log.

---

## Current Project Editing Rules

Work only inside the current new project repository.

Prefer small, clean changes.

Do not create extra files unless necessary.

Do not add broad documentation, raw debug artifacts, temporary reports, or sprawling intermediate outputs unless explicitly requested.

The new project should stay minimal, readable, and structurally clean.

---

## Windows Python Environment Rules

This project uses Python 3.11.9.

The project virtual environment path is:

`D:\minimal-space-simulated-listening\.venv`

All Python commands must use:

`.\.venv\Scripts\python.exe`

Do not use:

- bundled Python
- `python`
- `python3`
- `python3.11`
- global `pip`

Use this test command:

`.\.venv\Scripts\python.exe -m pytest`

Use this compile check:

`.\.venv\Scripts\python.exe -m compileall src`

If Windows sandbox reports:

`CryptUnprotectData failed: 2148073483`

Do not treat it as a broken `.venv`.
Report it as a Codex Windows sandbox issue, request user authorization, and continue only after authorization.

---

## Before Editing

Before making changes, state briefly:

1. which current files will be edited
2. whether `references/legacy_index.md` will be used
3. whether `D:\groove-ear` will be inspected
4. what legacy material will not be imported

Then proceed with the smallest useful change.
