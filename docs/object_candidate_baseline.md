# Object Candidate Baseline

Status: first minimal object-candidate layer after `ome_mapping_packet.json`.

This layer turns O/M/E candidate fields into provisional auditory object candidates:

```text
ome_mapping_packet.json
→ object-candidate baseline
→ object_candidate_packet.json
```

It does **not** perform temporal-spatial object tracking across multiple windows.
It does **not** confirm object identity.
It does **not** produce a listening report.
It does **not** perform source separation, instrument recognition, singer identification, ASR, lyric recognition, or human calibration.

The output is a candidate packet only.

---

## Script

```text
scripts/run_object_candidate_baseline.py
```

Default input:

```text
outputs/<input-stem>/ome_mapping_packet.json
```

Default output:

```text
outputs/<input-stem>/object_candidate_packet.json
```

Both files are generated local material and should stay ignored by git.

---

## Run

After generating `ome_mapping_packet.json`:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_object_candidate_baseline.py `
  --input "outputs\<input-stem>\ome_mapping_packet.json"
```

Optional explicit output path:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_object_candidate_baseline.py `
  --input "outputs\<input-stem>\ome_mapping_packet.json" `
  --output "outputs\<input-stem>\object_candidate_packet.json"
```

This script uses only the Python standard library.

---

## Candidate types

The baseline builder may emit these candidate types:

```text
rhythmic_pulse_candidate
transient_event_candidate
harmonic_layer_candidate
texture_mass_candidate
receiver_spread_layer_candidate
pressure_body_candidate
```

These names are internal object-candidate types, not final report language.

---

## Candidate structure

Every object candidate must include:

```text
object_id
candidate_type
status
activation
confidence
supporting_OME_fields
time_scope
spatial_proxy_state
continuity_inputs
relation_inputs
can_support
cannot_prove
next_required_step
```

This prevents the system from jumping from evidence to final interpretation.

---

## Candidate rules

### 1. rhythmic_pulse_candidate

Supporting fields:

```text
M-domain.pulse_transfer_candidate
object-candidate-input.rhythmic_object_input
```

Can support:

```text
repeated pulse candidate
impact-like recurrence candidate
input for later recurrence tracking
```

Cannot prove:

```text
drum identity
kick / snare / percussion identity
meter truth
groove quality
performance quality
```

---

### 2. transient_event_candidate

Supporting fields:

```text
object-candidate-input.transient_activity_input
M-domain.pulse_transfer_candidate
M-domain.activity_continuity_candidate
```

Can support:

```text
sudden auditory event candidate
possible boundary marker
possible interruption candidate
```

Cannot prove:

```text
which source caused the transient
confirmed object boundary
object persistence
```

---

### 3. harmonic_layer_candidate

Supporting fields:

```text
O-space.source_side_harmonic_contour_candidate
object-candidate-input.harmonic_layer_input
O-space.source_side_timbre_shape_candidate
```

Can support:

```text
harmonic or tonal layer candidate
persistence input across future windows
recurring contour candidate
```

Cannot prove:

```text
key truth
melody truth
chord truth
instrument identity
voice identity
musical meaning
```

---

### 4. texture_mass_candidate

Supporting fields:

```text
O-space.source_side_spectral_density_candidate
O-space.source_side_timbre_shape_candidate
object-candidate-input.texture_mass_input
```

Can support:

```text
broad texture candidate
mass-like layer candidate
possible background / field layer input
```

Cannot prove:

```text
noise wall
pad
guitar
synth
crowd
vocal texture identity
report metaphor
```

---

### 5. receiver_spread_layer_candidate

Supporting fields:

```text
E-space.receiver_side_width_candidate
E-space.receiver_side_spread_candidate
E-space.receiver_side_lr_balance_candidate
```

Can support:

```text
receiver-side spread candidate
side-layer candidate
spatial proxy for later object binding
```

Cannot prove:

```text
physical source width
real physical 3D location
room geometry
speaker placement
HRTF
surround field
```

---

### 6. pressure_body_candidate

Supporting fields:

```text
M-domain.pressure_transfer_candidate
E-space.receiver_side_perceived_pressure_candidate
O-space.source_side_spectral_density_candidate
```

Can support:

```text
pressure-bearing body candidate
foreground-weight input
possible presses-forward relation after tracking
```

Cannot prove:

```text
near distance
emotional intensity
physical body
source identity
```

---

## Why this layer exists

The mechanism-to-OME layer says:

```text
this evidence can support this O/M/E field
```

The object-candidate layer says:

```text
these O/M/E fields may belong together as a provisional auditory object candidate
```

It still does not say:

```text
this object persisted
this object moved
this object masked another object
this object is a vocal / drum / synth / guitar
this is how the final listening report should describe it
```

Those require later stages.

---

## Next step

The next layer should be:

```text
temporal-spatial-object-tracking-baseline
```

It should compare multiple `object_candidate_packet.json` files or multiple window packets and produce:

```text
track_id
object_candidate_ids
window_sequence
persistence_score
spatial_continuity_score
mechanism_continuity_score
relations
uncertainty
cannot_prove
```

Still no final listening report yet.
