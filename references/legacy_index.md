# Legacy Reference Index

## Legacy Project Location

The legacy project is an optional local reference archive.

This repository does not require the legacy archive to run.

If a contributor has a local copy of the legacy Groove Ear archive, record it as a machine-specific path outside git, or refer to it in this document using:

```text
<legacy-project-path>
```

This directory, when available, must be treated as a read-only reference archive.

It is not the current project root.

The current project is a clean rebuild. The current source of truth is the new project `README.md`.

---

## Purpose

This file explains how to consult the old Groove Ear project without accidentally reviving its structure.

The legacy project may be used as background material for:

- historical concepts
- terminology
- previous modeling attempts
- earlier experiments
- useful fragments that may inspire the new design

It must not be used as the current project baseline.

---

## Reference Priority

When working on the new project, use this authority order:

1. `README.md`
2. current files in the new repository
3. this file, `references/legacy_index.md`
4. selected legacy files under `<legacy-project-path>`, only when such an archive is available and explicitly needed

If any legacy material conflicts with the new `README.md`, the new `README.md` wins.

---

## Allowed Legacy Use

Codex may read legacy files under an explicitly provided local legacy archive path.

Allowed use includes:

- understanding why earlier versions existed
- checking old terminology
- comparing old and new concepts
- extracting a useful idea, method, or phrase
- summarizing old experiments as background

Legacy material should normally be rewritten, simplified, or conceptually referenced before entering the new project.

Direct copying should be rare and must be explicitly justified.

---

## Forbidden Legacy Use

Codex must not:

- modify anything under the local legacy archive
- delete anything under the local legacy archive
- rename anything under the local legacy archive
- reformat anything under the local legacy archive
- write new files under the local legacy archive
- treat the local legacy archive as the current project root
- rebuild the old folder structure
- continue old V1/V2/V3 architecture by default
- import old debug outputs
- import unnecessary intermediate artifacts
- copy large old files into the new project
- use old files to override the new README

---

## How To Consult Legacy Files

Before reading legacy files, Codex should state:

1. why legacy reference is needed
2. which local legacy archive path will be used
3. which part of the legacy project may be relevant
4. what will not be imported from the old project

After reading legacy files, Codex should state:

1. which files were consulted
2. what useful essence was extracted
3. whether anything was migrated into the new project
4. whether `docs/migration_log.md` was updated

---

## Suggested Legacy Areas To Check

Use this section as a lightweight map. Add concrete paths later only after confirming they are still useful.

Possible reference areas:

- old README files
- old project-state documents
- old protocol documents
- old source-field or projection-field documents
- old playback or listening reports
- old scripts, only for understanding previous experiments

Old scripts should be treated as historical experiments, not as current implementation templates.

---

## Migration Requirement

If any legacy material is reused in the new project, update:

`docs/migration_log.md`

The migration log must record:

- source legacy path
- reused content or idea
- migration type
- reason for inclusion
- target file in the new project

If legacy material was only inspected but not reused, mention it in the task summary but do not add a migration entry.
