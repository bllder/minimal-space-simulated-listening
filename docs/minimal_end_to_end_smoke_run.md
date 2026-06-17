# Minimal End-to-End Smoke Run

Status: engineering smoke check.

This document describes the first local end-to-end MSSL pipeline check.
It verifies that the current baseline scripts can connect from an audio input to an auditory scene graph packet.

It is not a listening report.
It is not human calibration.
It is not an optional-adapter runtime.
It does not commit audio files or generated outputs.

---

## Pipeline under test

```text
local audio file
→ audio_evidence_packet.json
→ ome_mapping_packet.json
→ object_candidate_packet.json
→ object_track_packet.json
→ auditory_scene_graph_packet.json
```

The smoke runner uses the existing baseline scripts:

```text
scripts/run_librosa_baseline_evidence.py
scripts/run_mechanism_to_ome_baseline.py
scripts/run_object_candidate_baseline.py
scripts/run_temporal_spatial_object_tracking_baseline.py
scripts/run_auditory_scene_graph_baseline.py
```

---

## Default synthetic run

Use this first.
It generates a small local synthetic WAV under `outputs/`, splits it into two ordered windows, and runs the full packet chain.

Windows:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_minimal_pipeline_smoke.py --generate-synthetic --output-dir outputs
```

macOS / Linux:

```bash
./.venv/bin/python ./scripts/run_minimal_pipeline_smoke.py --generate-synthetic --output-dir outputs
```

---

## Local audio run

Use this only after the synthetic run works.
The audio file stays local and must not be committed.

Windows:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_minimal_pipeline_smoke.py --input "path\to\local_audio.wav" --output-dir outputs
```

macOS / Linux:

```bash
./.venv/bin/python ./scripts/run_minimal_pipeline_smoke.py --input "path/to/local_audio.wav" --output-dir outputs
```

---

## Expected local outputs

Default synthetic run writes under:

```text
outputs/minimal_pipeline_smoke/
```

Expected layout:

```text
outputs/minimal_pipeline_smoke/
  synthetic_smoke_test.wav
  window_00/
    audio_evidence_packet.json
    ome_mapping_packet.json
    object_candidate_packet.json
  window_01/
    audio_evidence_packet.json
    ome_mapping_packet.json
    object_candidate_packet.json
  object_track_packet.json
  auditory_scene_graph_packet.json
  minimal_pipeline_smoke_summary.json
```

All files under `outputs/` are generated local artifacts and should remain ignored by git.

---

## What is checked

The smoke runner checks that each expected packet exists and has the expected schema:

```text
mssl_audio_evidence_packet_v0_1_librosa_baseline
mssl_mechanism_to_ome_mapping_v0_1
mssl_object_candidate_packet_v0_1
mssl_object_track_packet_v0_1
mssl_auditory_scene_graph_packet_v0_1
```

It writes a local summary packet:

```text
minimal_pipeline_smoke_summary.json
```

---

## What this does not prove

A passing smoke run does not prove:

```text
human-quality listening interpretation
correct object identity
physical source localization
instrument identity
singer identity
lyrics
emotion
genre
taste
```

It only proves that the current minimal engineering chain can run from local audio to a scene-graph candidate packet.

---

## Dependency note

The first stage uses `scripts/run_librosa_baseline_evidence.py`, so the local Python environment must have the baseline dependency installed.

Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install librosa
```

macOS / Linux:

```bash
./.venv/bin/python -m pip install librosa
```

Do not install optional adapter dependencies for this smoke run.
