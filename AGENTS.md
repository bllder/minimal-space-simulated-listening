# AGENTS.md

## Project Status

This repository is a clean rebuild.

The current formal project name is:

**Minimal Space for Simulated Listening**

“Groove Ear” is a historical codename and may appear in legacy materials.

The current project source of truth is:

1. `README.md`
2. `AGENTS.md`
3. current files in this repository
4. legacy materials only when explicitly referenced through `references/legacy_index.md`

If any legacy material conflicts with `README.md` or `AGENTS.md`, the current repository files win.

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

## Branch / Mainline Rule

Work on `main` unless the user explicitly says to create a branch.

Do not create branches, PRs, or parallel worktrees by default. Keep changes small and commit them directly to the mainline.

---

## MSSL Core Boundary

This project builds a traceable simulation path from audio evidence to bounded human-readable listening language.

MSSL must not silently become:

- an unbounded music review generator
- a fixed listening-report renderer
- a genre classifier
- an emotion classifier
- a taste or recommendation system
- a singer or exact instrument identity system
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
- listening-experience evidence pack
- critical listening brief
- aesthetic context handoff
- bounded close-listening criticism

The listening-experience layer may use human listening language only when it is a bounded rendering of evidence, adapter output, user-supplied context, external context, or explicit backend reasoning.

---

## Current Runtime Boundary

Current normal path:

```text
local PCM WAV
-> structural audio evidence
-> O/M/E listening-space simulation
-> object / relation / scene evidence
-> listening-experience evidence pack
-> critical_listening_brief.json
-> aesthetic context handoff section when context is provided
-> online AI handoff
-> bounded human-readable close-listening criticism
```

The repository prepares evidence and handoff material. It does not claim that the local script has personally heard the song, and it does not turn genre-like, emotion-like, source-family, memory, comment, or playlist-context language into truth labels.

Final prose may be generated only by a clearly enabled LLM/backend stage or by pasting `online_ai_listening_handoff.md` into an online AI account.

---

## Aesthetic Context Boundary

MSSL must not try to make human listening language emerge from denser internal structure.

The human-facing layer may start from:

- user aesthetic seed files
- playlist names and playlist type
- user notes, comments, or memory anchors
- platform comments with timestamp/context boundaries
- lyrics or lyric alignment when available
- reviews, metadata, label/version context
- MIR or external adapter notes

MSSL then constrains the interpretation.

Do not poetically interpret playlist names before classification. First classify the context as private naming, style cluster, label entry, single-work research, test/probe set, memory anchor, external metadata, or unknown.

Examples:

```text
神圣骨头 = Sacred Bones Records label entry
Starless = King Crimson "Starless" version/material research
Test.py / Math AI = test/probe set
```

---

## Cross-Modal Listening Boundary

Music is not treated as an isolated spatial-auditory object.

MSSL may support explicit interfaces into:

- body response: pressure, looseness, heaviness, floating, wakefulness, numbness, being held, being pushed away
- image / scene: color, light, room, weather, road, face, medium image
- memory / timestamp: platform comments, private notes, version memory, medium memory
- playlist / context: private naming, style cluster, label entry, single-work research, material type, test set, or memory anchor

These interfaces are not free invention. They must be bounded by evidence or user-supplied context.

NetEase / platform comments and private comments are often timestamped memory material. Do not treat them as present-tense crisis signals without timestamp and context.

Playlist names must be disambiguated before interpretation. Do not poeticize every playlist name by default.

Do not use emergence language to hand-wave missing mechanisms. Add explicit interfaces instead.

---

## Output Boundary

Generated summaries and Markdown outputs must clearly distinguish:

- structural understanding
- readable structural rendering
- critical listening brief
- aesthetic context handoff
- bounded close-listening criticism
- human calibration
- comment-data analysis

Any major natural-language claim should be traceable to packet evidence or a clearly marked context source.

Default generated outputs remain local artifacts unless a future task explicitly promotes a curated example.

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

Do not add broad documentation, raw debug artifacts, temporary reports, or sprawling intermediate outputs unless explicitly requested.

The new project should stay minimal, readable, and structurally clean.

---

## Python Environment Rules

This project should be runnable from any cloned project folder.
