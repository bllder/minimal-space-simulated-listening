# Migration Log

This file records legacy material that has been intentionally reused in the clean rebuild of:

**Minimal Space for Simulated Listening**

The legacy project is located at:

`D:\groove-ear`

Legacy materials are reference only.

The current project source of truth remains:

1. `README.md`
2. current files in this new repository

---

## How To Use This Log

Add one entry only when material from the legacy project is actually reused in the new project.

Do not add an entry if legacy material was only inspected but not imported, rewritten, summarized, or conceptually adopted.

Each entry should answer:

- Where did it come from?
- What was reused?
- How was it reused?
- Why does it belong in the new project?
- Where did it go?

---

## Entry Template

```md
## YYYY-MM-DD — Short migration title

### Legacy source

`D:\groove-ear\path\to\legacy_file.md`

### Reused material

Briefly describe the concept, phrase, code idea, structure, or note that was reused.

### Migration type

Choose one:

- copied
- rewritten
- summarized
- conceptually referenced
- adapted into new structure

### Reason

Explain why this legacy material belongs in the clean rebuild.

### Target file

`path\to\current_project_file.md`

### Notes

Mention anything intentionally not imported from the legacy source.
```

---

## Migration Entries

No legacy material has been migrated yet.

## 2026-06-15 - V3 temporal-spatial auditory object tracking

### Current source
Current clean rebuild working copy and the 42s-50s selected validation clip.

### Reused material
No legacy project structure was imported. This update extends the current V2.2 validation output.

### Migration type
Conceptual extension + report/schema revision.

### Current destination
- `scripts/run_first_validation.py`
- `outputs/mapping_packet.json`
- `outputs/listening_report.md`
- `outputs/baseline_features.json`
- `docs/temporal_spatial_object_tracking.md`

### Why it belongs
MSSL needs to move from a visualized listening field to trackable auditory objects. Sound objects persist across intervals; they are not isolated single-frame labels.

### What was intentionally not imported
- No source separation
- No automatic instrument recognition
- No voice recognition
- No old project structure
- No audio terminology as the primary language
