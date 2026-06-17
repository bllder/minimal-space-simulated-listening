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
4. If legacy reference is needed, ask for or use the local legacy archive path recorded in `references/legacy_index.md`.
5. Treat any legacy archive as read-only background material.
6. Extract only the useful essence from legacy materials.
7. Rewrite, simplify, or adapt legacy ideas into the new project.
8. Do not directly revive old project structure, old architecture, or old output sprawl.
9. If any legacy material is reused, update `docs/migration_log.md`.
10. Summarize what was changed, what legacy material was consulted, and what was intentionally not imported.

---

## Legacy Project Rules

The legacy project is an optional local reference archive.

It is not required to run this repository.

If a local legacy archive is available, record its path in `references/legacy_index.md` using a machine-specific placeholder such as:

```text
<legacy-project-path>
```

Codex may read files under that path for:

- historical concepts
- terminology
- earlier experiments
- old modeling attempts
- useful background context

Codex must not:

- modify anything under the local legacy archive
- delete anything under the local legacy archive
- rename anything under the local legacy archive
- reformat anything under the local legacy archive
- write new files under the local legacy archive
- treat the local legacy archive as the current project root
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

## Python Environment Rules

This project should be runnable from any cloned project folder.

Create the virtual environment inside the project root:

```text
<project-root>/.venv
```

On Windows, prefer:

```powershell
.\.venv\Scripts\python.exe
```

On macOS / Linux, prefer:

```bash
./.venv/bin/python
```

Do not use:

- bundled Python
- an unrelated global Python
- global `pip`

Use the venv Python for tests and checks.

Windows examples:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m compileall scripts
```

macOS / Linux examples:

```bash
./.venv/bin/python -m pytest
./.venv/bin/python -m compileall scripts
```

If Windows sandbox reports:

`CryptUnprotectData failed: 2148073483`

Do not treat it as a broken `.venv`.
Report it as a Codex Windows sandbox issue, request user authorization, and continue only after authorization.

---

## Before Editing

Before making changes, state briefly:

1. which current files will be edited
2. whether `references/legacy_index.md` will be used
3. whether a local legacy archive will be inspected
4. what legacy material will not be imported

Then proceed with the smallest useful change.
