# Readable Structural Summary Renderer

Status: structural rendering documentation.

This document describes the standalone renderer:

```text
scripts/render_readable_structural_summary.py
```

It is a small Markdown renderer for existing MSSL packets. It does not modify
the main pipeline.

## Input

The renderer reads packets from one run directory by default:

```text
music_understanding_summary.json
auditory_scene_graph_packet.json
object_track_packet.json
auditory_hypothesis_packet.json  # optional
```

The preferred input is `music_understanding_summary.json` because it already
aggregates structure and relation readings. If that file is absent, the renderer
falls back to `auditory_scene_graph_packet.json` and then
`object_track_packet.json` where possible.

## Output

Default output:

```text
readable_structural_summary.md
```

The first line of the Markdown output is always:

```text
Status: structural summary only. This is not a listening report.
```

The output includes packet input status, a `Field sketch`, structural
rendering, relation rendering, optional auditory hypothesis support, a boundary
note, and an `Evidence anchors` section.

## Insertion Position

This renderer sits after existing packet generation:

```text
object_track_packet.json
+ auditory_scene_graph_packet.json
+ music_understanding_summary.json
+ optional auditory_hypothesis_packet.json
-> readable_structural_summary.md
-> STOP before listening report
```

It is not called by the current main pipeline. Run it manually against a packet
directory when a readable structural rendering is needed.

## Why This Is Not A Listening Report

The renderer only rewords packet-backed structural data. It can render bounded
terms such as:

```text
sustained layer
transient event
texture mass
pressure body
receiver spread field
rhythmic anchor
dominant / supporting / weak
persistent / recurring / local / background
relation / containment / co-presence / support
```

Every major rendered statement carries an evidence anchor that points back to a
packet and field path. The renderer does not add free-form listening-report
language or human-calibrated interpretation.

Field sketch is still packet-backed structural rendering, not a listening
report.

## How To Run Locally

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe .\scripts\render_readable_structural_summary.py `
  --run-dir outputs\reference_probe_bank\harmonic_layer_plus_pulse\mssl_output
```

Explicit output path:

```powershell
.\.venv\Scripts\python.exe .\scripts\render_readable_structural_summary.py `
  --run-dir outputs\reference_probe_bank\harmonic_layer_plus_pulse\mssl_output `
  --output outputs\reference_probe_bank\harmonic_layer_plus_pulse\mssl_output\readable_structural_summary.md
```

## Boundary

Allowed output scope:

```text
structural explanation
packet-backed readable rendering
time / space / layer structure
object and relation evidence
```

Not allowed:

```text
genre / style classification
taste judgment
emotion claim
singer identity
instrument identity
lyrics / ASR / semantic song meaning
comment-data analysis
music generation
human calibration
```

Generated Markdown is a local validation or inspection artifact unless a task
explicitly asks to commit a fixture. Do not commit `outputs/`, audio files,
datasets, comment data, caches, or local validation artifacts.
