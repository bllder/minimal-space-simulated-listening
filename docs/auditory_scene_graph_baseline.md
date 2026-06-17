# Auditory Scene Graph Baseline

Status: first graph layer after `object_track_packet.json`.

This layer turns object tracks into a provisional auditory scene graph:

```text
object_track_packet.json
→ auditory scene graph baseline
→ auditory_scene_graph_packet.json
```

It does **not** produce a final listening report.
It does **not** perform human calibration.
It does **not** identify sources, singers, instruments, lyrics, genre, mood, or taste.

---

## Script

```text
scripts/run_auditory_scene_graph_baseline.py
```

Default input:

```text
object_track_packet.json
```

Default output:

```text
auditory_scene_graph_packet.json
```

Generated outputs should remain local and ignored by git.

---

## Run

Windows:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_auditory_scene_graph_baseline.py `
  --input "outputs\object_track_packet.json" `
  --output "outputs\auditory_scene_graph_packet.json"
```

macOS / Linux:

```bash
./.venv/bin/python ./scripts/run_auditory_scene_graph_baseline.py \
  --input "outputs/object_track_packet.json" \
  --output "outputs/auditory_scene_graph_packet.json"
```

---

## Output groups

```text
graph.nodes
graph.edges
graph.scene_summary_candidates
audit
```

---

## Node candidates

Each object track becomes a scene node candidate.

Node roles may include:

```text
event_anchor_candidate
event_detail_candidate
foreground_pressure_candidate
pressure_shadow_candidate
receiver_space_field_candidate
background_or_field_mass_candidate
texture_event_candidate
harmonic_layer_candidate
harmonic_fragment_candidate
untyped_scene_node_candidate
```

These are internal graph roles.
They are not final report wording.

---

## Edge candidates

The baseline graph builder may emit relation candidates such as:

```text
event_against_field_candidate
field_contains_event_candidate
pressure_inside_spread_field_candidate
spread_field_around_pressure_candidate
harmonic_layer_over_texture_candidate
texture_under_harmonic_layer_candidate
co_present_candidate
strengthens_across_windows
weakens_across_windows
roughly_stable_across_windows
appears_or_disappears_between_windows
```

These relations describe possible graph structure.
They do not prove physical containment, masking, movement, or meaning.

---

## Why this layer exists

Previous layers build:

```text
audio evidence
→ O/M/E candidates
→ object candidates
→ object tracks
```

This layer asks:

```text
Which tracks may behave as scene nodes?
Which tracks may relate to each other?
Which roles are likely foreground, field, event, pressure, texture, or harmonic layer?
```

It still does not ask:

```text
How should the user-facing listening report describe the song?
What is the human-validated listening center?
What is the musical meaning?
```

---

## Boundary

Every node and edge remains a candidate.

Required caution:

```text
node ≠ confirmed physical sound source
edge ≠ human-validated relation
foreground/background ≠ final perceptual truth
scene graph ≠ listening report
```

---

## Next step

The next layer should be a controlled report boundary, not a loose automatic music review.

Recommended next step:

```text
calibrated-report-boundary
```

It should decide how `auditory_scene_graph_packet.json` may be converted into human-readable language without introducing tag leakage, comment leakage, genre judgment, or taste scoring.

Optional adapters should still remain separate:

```text
Essentia selected modules
Basic Pitch optional adapter
Demucs optional adapter
```
