# Public Sample Selection Workflow

Status: selection workflow only.

This document defines how MSSL should choose public validation samples without adding audio files or generated song outputs to the repository.

---

## Purpose

The public sample layer exists to test the minimum runnable pipeline:

```text
audio file
→ audio_evidence_packet.json
→ ome_mapping_packet.json
→ object_candidate_packet.json
```

It is not for taste training, style scoring, or report-language training.

---

## Target set

```text
FMA: 3 samples
MTG-Jamendo: 2 samples
```

Use this order:

```text
1. Pick candidate sample metadata.
2. Review source and license fields.
3. Download audio locally only.
4. Run the MSSL baseline pipeline locally.
5. Keep generated outputs local unless a future PR explicitly approves a tiny example artifact.
```

---

## Selection criteria

Choose samples that stress different parts of the current baseline:

```text
sample 1: clear rhythm / onset behavior
sample 2: harmonic or tonal layer behavior
sample 3: stereo width / spread behavior
sample 4: texture or density behavior
sample 5: external tag comparison boundary
```

The goal is diversity of evidence behavior, not musical preference.

---

## What can be committed

Allowed:

```text
metadata-only manifest
dataset source name
track ID or source page
license note
why the sample was selected
which MSSL evidence path it tests
```

Not allowed by default:

```text
audio files
large dataset files
generated stems
generated MIDI
generated reports
comment data
song-specific listening-language profiles
```

---

## Required review before filling a sample slot

Each sample slot must answer:

```text
1. Which dataset is it from?
2. What is the source track ID or page?
3. What is the license string?
4. Is redistribution allowed?
5. Are we committing audio? Default: no.
6. Are we committing generated output? Default: no.
7. Which part of the baseline pipeline does it test?
8. Could the dataset tag leak into MSSL report language?
```

---

## Local run example

Run from project root.

```powershell
.\.venv\Scripts\python.exe .\scripts\run_librosa_baseline_evidence.py --input "path\to\local_audio.wav" --output-dir outputs
.\.venv\Scripts\python.exe .\scripts\run_mechanism_to_ome_baseline.py --input "outputs\<input-stem>\audio_evidence_packet.json"
.\.venv\Scripts\python.exe .\scripts\run_object_candidate_baseline.py --input "outputs\<input-stem>\ome_mapping_packet.json"
```

macOS / Linux:

```bash
./.venv/bin/python ./scripts/run_librosa_baseline_evidence.py --input "path/to/local_audio.wav" --output-dir outputs
./.venv/bin/python ./scripts/run_mechanism_to_ome_baseline.py --input "outputs/<input-stem>/audio_evidence_packet.json"
./.venv/bin/python ./scripts/run_object_candidate_baseline.py --input "outputs/<input-stem>/ome_mapping_packet.json"
```
