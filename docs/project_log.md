# Project Log

This file records current-project development notes that are not legacy migrations.

Use `docs/migration_log.md` only when old Groove Ear material is intentionally reused.

---

## 2026-06-15 — V3 temporal-spatial auditory object tracking

### Source

Current clean rebuild working copy and the 42s-50s selected validation clip.

### Change type

Conceptual extension plus report/schema revision.

### Updated destinations

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

---

## 2026-06-17 — Repo hygiene and licensing boundary

### Source

Current public GitHub repository state.

### Change type

Repository hygiene.

### Updated destinations

- `LICENSE.md`
- `CITATION.cff`
- `NOTICE.md`
- `references/papers_index.md`
- `docs/project_log.md`
- `docs/migration_log.md`
- `.gitignore`

### Why it belongs

The project is now public on GitHub. It needs a licensing boundary, citation metadata, third-party reference discipline, and separation between current-project notes and legacy migration notes.

### What was intentionally not imported

- No third-party PDFs
- No copyrighted audio
- No generated outputs
- No old project structure
- No script logic changes

---

## 2026-06-17 — Minimal smoke validation

### Source

Current `main` branch after `scripts/run_minimal_pipeline_smoke.py` was merged.

### Change type

Engineering validation record.

### Result

Synthetic smoke run passed.

Local WAV smoke run passed.

The local smoke summary reported:

```text
schema: mssl_minimal_pipeline_smoke_summary_v0_1
status: passed
window_count: 2
checks: 8 / 8 passed
```

### Why it belongs

This records the first end-to-end proof that the current minimal MSSL chain can run from local audio to `auditory_scene_graph_packet.json`.

### What was intentionally not imported

- No audio files
- No generated outputs
- No listening report
- No human calibration
- No optional adapter runtime
- No external datasets
