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

## MSSL Core Boundary

This project builds structural understanding for simulated listening.

It must not be silently converted into:

- a music review generator
- a genre classifier
- an emotion classifier
- a taste or recommendation system
- a singer or instrument identity system
- a lyrics / ASR / semantic song-meaning system
- a scraped comment analysis system
- a music generation system
- a human calibration layer unless explicitly requested

Allowed core language:

- O / M / E source-to-receiver mapping
- audio evidence
- structural candidate
- auditory hypothesis
- temporal-spatial object tracking
- scene relation
- structural summary
- sustained layer
- transient event
- texture mass
- pressure body
- receiver spread field
- rhythmic anchor
- dominant / supporting / weak
- persistent / recurring / local / background
- relation / containment / co-presence / support

Readable language is allowed only when it is a bounded rendering of packet evidence.

Do not add free-form listening-report language unless the task explicitly asks for a separate listening-report layer.

---

## Output Boundary

Generated summaries and Markdown outputs must clearly distinguish:

- structural understanding
- readable structural rendering
- listening report
- human calibration
- comment-data analysis

Default project outputs must remain structural-only.

If a task adds a human-readable renderer, it must state:

```text
Status: structural summary only. This is not a listening report.
```

Any major natural-language claim should be traceable to packet evidence such as:

- `audio_evidence_packet.json`
- `ome_mapping_packet.json`
- `object_candidate_packet.json`
- `auditory_hypothesis_packet.json`
- `object_track_packet.json`
- `auditory_scene_graph_packet.json`
- `music_understanding_summary.json`

---

## Repository Hygiene

Do not commit:

- `outputs/`
- audio files
- generated WAV / MP3 / FLAC files
- datasets
- scraped comments
- local cache files
- temporary validation artifacts
- local environment folders outside the intended project `.venv`

Generated files may be used for local validation, but they should not be committed unless the task explicitly requests a small reference fixture.

---

## Validation Report Requirements

Every implementation task must end with a short report containing:

1. changed files
2. commands run
3. generated files, if any
4. validation result
5. boundary check result
6. what was not done
7. known risks or follow-up tasks

If no tests exist, report that explicitly instead of inventing a test result.

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
