# Temporal-Spatial Object Tracking Baseline

Status: first baseline tracker after `object_candidate_packet.json`.

This layer compares multiple object-candidate packets and builds provisional object tracks:

```text
object_candidate_packet.json files
→ temporal-spatial object tracking baseline
→ object_track_packet.json
```

It does **not** produce a listening report.
It does **not** build the final auditory scene graph.
It does **not** confirm source identity or physical movement.
It does **not** perform human calibration.

---

## Script

```text
scripts/run_temporal_spatial_object_tracking_baseline.py
```

Default output:

```text
object_track_packet.json
```

or, when all inputs share a folder:

```text
outputs/<input-stem>/object_track_packet.json
```

Generated outputs should remain local and ignored by git.

---

## Run with explicit ordered inputs

Use this when window order matters:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_temporal_spatial_object_tracking_baseline.py `
  --inputs "outputs\window_01\object_candidate_packet.json" "outputs\window_02\object_candidate_packet.json" `
  --output "outputs\object_track_packet.json"
```

macOS / Linux:

```bash
./.venv/bin/python ./scripts/run_temporal_spatial_object_tracking_baseline.py \
  --inputs "outputs/window_01/object_candidate_packet.json" "outputs/window_02/object_candidate_packet.json" \
  --output "outputs/object_track_packet.json"
```

---

## Run by directory scan

```powershell
.\.venv\Scripts\python.exe .\scripts\run_temporal_spatial_object_tracking_baseline.py `
  --input-dir outputs
```

This recursively finds files named:

```text
object_candidate_packet.json
```

For strict experiments, explicit `--inputs` is preferred because directory ordering is only lexical.

---

## Output groups

```text
windows
tracks
audit
```

Each track contains:

```text
track_id
candidate_type
status
observation_count
observed_window_indices
persistence_score
activation_mean
activation_delta
confidence_mean
mechanism_continuity_score
spatial_continuity_score
window_sequence
relations
can_support
cannot_prove
next_required_step
```

---

## Baseline matching rule

The first tracker groups observations by:

```text
candidate_type across ordered windows
```

This is intentionally simple. It makes the first temporal connection possible without pretending to solve source identity.

Example:

```text
rhythmic_pulse_candidate in window 1
rhythmic_pulse_candidate in window 2
rhythmic_pulse_candidate in window 3
→ track_rhythmic_pulse_candidate
```

This can support persistence evidence.
It cannot prove that the same physical source produced every observation.

---

## Scores

### persistence_score

```text
observed windows / total windows
```

Can support:

```text
candidate appears repeatedly
candidate may persist across time
```

Cannot prove:

```text
confirmed object identity
physical source persistence
```

### activation_delta

```text
last activation - first activation
```

Can support:

```text
strengthens_across_windows
weakens_across_windows
roughly_stable_across_windows
```

Cannot prove:

```text
intentional musical development
emotion
performance quality
```

### mechanism_continuity_score

Compares supporting O/M/E field values between adjacent observations.

Can support:

```text
feature-backed continuity proxy
stable mechanism behavior across windows
```

Cannot prove:

```text
true source identity
human-recognized object sameness
```

### spatial_continuity_score

Compares receiver-side spatial proxy descriptions.

Can support:

```text
receiver-side proxy consistency
candidate spatial-state continuity
```

Cannot prove:

```text
real physical 3D movement
room geometry
speaker placement
```

---

## Relation candidates

The baseline tracker may emit relation candidates such as:

```text
strengthens_across_windows
weakens_across_windows
roughly_stable_across_windows
appears_or_disappears_between_windows
may_support_event_recurrence
may_support_layer_persistence
may_support_receiver_side_spread_continuity
```

These are relation candidates only.
They are not final listening-report sentences.

---

## Why this layer exists

Previous layers say:

```text
audio evidence → O/M/E candidates → object candidates
```

This layer asks:

```text
Do similar object candidates recur across ordered windows?
Do their activation and proxy states change?
Can they become track candidates for an auditory scene graph?
```

It still does not answer:

```text
What is the final scene?
What should a listener feel?
What should the final report say?
```

---

## Next step

The next layer should be:

```text
auditory-scene-graph-baseline
```

It should read `object_track_packet.json` and build relation structure such as:

```text
track nodes
supporting windows
foreground/background candidates
masking or filling candidates
pressure/spread relations
uncertainty
cannot_prove
```

Still no final public listening report until the calibration/report layer is intentionally added.
