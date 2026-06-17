# Music Understanding Summary

Status: structural understanding layer.

This layer translates MSSL object tracks and auditory scene graph packets into a readable structural summary.
It is not a final listening report and does not perform human calibration.

---

## Why this layer exists

The baseline chain can already produce machine packets:

```text
audio
→ audio_evidence_packet.json
→ ome_mapping_packet.json
→ object_candidate_packet.json
→ object_track_packet.json
→ auditory_scene_graph_packet.json
```

Those packets are useful for machines, but hard to read as product-facing diagnostics.
The music understanding summary explains what structural candidates MSSL found:

```text
persistent layer
recurring event
pressure body
receiver-side spread
texture field
scene relation
```

It answers:

```text
What does the machine think is structurally happening here?
```

It does not answer:

```text
What does this song emotionally mean?
Is this good music?
What genre is it?
Which instrument or singer is this?
```

---

## Position in the pipeline

```text
object_track_packet.json
+ auditory_scene_graph_packet.json
→ music_understanding_summary.json
→ music_understanding_summary.md
→ STOP before listening report
```

This layer sits after the scene graph and before any human-calibrated listening report.

---

## Command

After a minimal smoke run or reference probe run, point the script at the directory containing both:

```text
object_track_packet.json
auditory_scene_graph_packet.json
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_music_understanding_summary.py --run-dir outputs\minimal_pipeline_smoke
```

macOS / Linux:

```bash
./.venv/bin/python ./scripts/run_music_understanding_summary.py --run-dir outputs/minimal_pipeline_smoke
```

For a reference probe:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_music_understanding_summary.py --run-dir outputs\reference_probe_bank\major_triad_C4\mssl_output
```

Explicit packet paths are also supported:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_music_understanding_summary.py `
  --object-track outputs\minimal_pipeline_smoke\object_track_packet.json `
  --scene-graph outputs\minimal_pipeline_smoke\auditory_scene_graph_packet.json `
  --output-dir outputs\minimal_pipeline_smoke
```

---

## Outputs

```text
music_understanding_summary.json
music_understanding_summary.md
```

The JSON output is machine-readable.
The Markdown output is for human inspection.

---

## What the summary contains

The summary includes:

```text
overview
primary structures
scene relations
time flow reading
space reading
layer reading
module diagnostics
report boundary
```

Example structural categories:

```text
harmonic_layer_candidate
texture_mass_candidate
transient_event_candidate
rhythmic_pulse_candidate
pressure_body_candidate
receiver_spread_layer_candidate
```

The summary explains these categories in structural language, such as:

```text
stable tonal or harmonic layer
texture or field mass
transient event anchor
rhythmic pulse or body-time anchor
pressure or low-body candidate
receiver-side spread field
```

---

## Boundary

Allowed:

```text
structural explanation
machine-readable diagnostic language
time/space/layer reading
object and relation explanation
```

Not allowed:

```text
final listening report
music review
emotion judgment
genre label
instrument identity
singer identity
lyrics or ASR
music generation
```

The output must keep the report boundary visible:

```text
This layer explains structural candidates found by MSSL, but it is not human-calibrated listening language.
```

---

## Product interpretation

For product work, this layer can be understood as:

```text
machine packet → product-readable structural diagnostic
```

It is the bridge between JSON packets and future human-facing listening language.

It should make it possible to inspect whether MSSL is seeing:

```text
what persists
what recurs
what presses forward
what spreads in receiver space
what behaves like a layer
what behaves like an event
what relations exist between candidates
```

without prematurely claiming that the system understands emotional meaning or musical intention.
